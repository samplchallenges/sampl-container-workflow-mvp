import logging
import tempfile
from pathlib import Path

import dask
import dask.distributed as dd
import ever_given.wrapper

from core import models

from . import scoring

logger = logging.getLogger(__name__)


def run_and_score_submission(client, submission):
    """
    Runs public and private, plus scoring
    """
    challenge = submission.challenge
    delayed_conditional = True
    for is_public in (True, False):
        element_ids = challenge.inputelement_set.filter(
            is_public=is_public
        ).values_list("id", flat=True)
        run_id, prediction_ids = run_submission(
            submission.pk, element_ids, delayed_conditional, is_public=is_public
        )
        delayed_conditional = check_and_score(run_id, prediction_ids)

    future = client.submit(delayed_conditional.compute)  # pylint:disable=no-member
    logger.info("Future key: %s", future.key)

    dd.fire_and_forget(future)
    return future


@dask.delayed(pure=False)  # pylint:disable=no-value-for-parameter
def check_and_score(submission_run_id, prediction_ids):  # pylint: disable=W0613
    submission_run = models.SubmissionRun.objects.get(pk=submission_run_id)
    submission_run.status = models.Status.SUCCESS
    submission_run.save()

    logger.info(
        "Running check_and_score %s public? %s",
        submission_run_id,
        submission_run.is_public,
    )
    scoring.score_submission(submission_run.submission.pk, submission_run_id)
    return True


@dask.delayed(pure=False)  # pylint:disable=no-value-for-parameter
def create_submission_run(submission_id, conditional, *, is_public):
    # conditional will be a dask delayed; if it's false, the run_element will no-op
    if not conditional:
        return
    submission = models.Submission.objects.get(pk=submission_id)
    container = submission.container
    if not container.digest:
        container.digest = "nodigest"
        container.save()
    submission_run = models.SubmissionRun.objects.create(
        submission=submission,
        digest=container.digest,
        is_public=is_public,
        status=models.Status.PENDING,
    )
    # TODO: need to store future key?
    # submission run pair is place to store?
    # submission_run.digest = future.key
    submission_run.save()
    return submission_run.id


def run_submission(submission_id, element_ids, conditional, is_public=True):

    submission_run_id = create_submission_run(
        submission_id, conditional, is_public=is_public
    )
    delayed_element_runs = dask.delayed(
        [
            run_element(
                submission_id,
                element_id,
                submission_run_id,
                is_public=is_public,
            )
            for element_id in element_ids
        ],
        nout=len(element_ids),
    )
    return (submission_run_id, delayed_element_runs)


@dask.delayed(pure=False)  # pylint:disable=no-value-for-parameter
def run_element(submission_id, element_id, submission_run_id, is_public):
    submission = models.Submission.objects.get(pk=submission_id)
    challenge = submission.challenge
    submission_run = submission.submissionrun_set.get(pk=submission_run_id)
    evaluation_score_types = {
        score_type.key: score_type
        for score_type in challenge.scoretype_set.filter(
            level=models.ScoreType.Level.EVALUATION
        )
    }

    element = challenge.inputelement_set.get(pk=element_id, is_public=is_public)

    output_file_keys = challenge.output_file_keys()

    container = submission.container

    evaluation = models.Evaluation.objects.create(
        input_element=element, submission_run=submission_run
    )

    kwargs, file_kwargs = element.all_values()
    evaluation.mark_started(kwargs, file_kwargs)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            dirpath = Path(str(tmpdir))
            output_dir = None
            if output_file_keys:
                output_dir = dirpath / "output"
                output_dir.mkdir()
            parsed_results = ever_given.wrapper.run(
                container.uri,
                kwargs=kwargs,
                file_kwargs=file_kwargs,
                output_dir=output_dir,
                output_file_keys=output_file_keys,
                log_handler=models.Evaluation.LogHandler(evaluation),
            )

            for key, value in parsed_results:
                output_type = challenge.output_type(key)
                if output_type:
                    prediction = models.Prediction.load_output(
                        challenge, evaluation, output_type, value
                    )
                    evaluation.append(stdout=f"{prediction.__dict__}")
                    prediction.save()
                else:
                    evaluation.append(stderr=f"Ignoring key {key} with value {value}")
        try:
            scoring.score_evaluation(
                challenge.scoremaker.container,
                evaluation,
                evaluation_score_types,
            )
        except Exception as exc:
            evaluation.append(stderr="Error scoring\n" f"{exc}")
            evaluation.save(update_fields=["log_stderr"])
            raise
        evaluation.status = models.Status.SUCCESS
    except Exception as exc:
        evaluation.status = models.Status.FAILURE
        evaluation.append(stderr=f"Execution failure: {exc}")
        raise
    finally:
        evaluation.save()
