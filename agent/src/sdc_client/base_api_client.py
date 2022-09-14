from abc import abstractmethod, ABC

import os
import urllib.parse
import inject
from sdc_client.interfaces import ILogger, IStreamSets

PREVIEW_TIMEOUT = os.environ.get('STREAMSETS_PREVIEW_TIMEOUT', 30000)


class _BaseStreamSetsApiClient(ABC):
    logger = inject.attr(ILogger)

    def __init__(self, streamsets_: IStreamSets):
        self.base_url = streamsets_.get_url()
        self.streamsets = streamsets_
        self.session = None

    @abstractmethod
    def _get_session(self):
        raise NotImplementedError

    def _build_url(self, *args):
        return urllib.parse.urljoin(self.base_url, '/'.join(['/rest/v1', *args]))

    def create_pipeline(self, name: str):
        self.logger.info(f'Create pipeline `{name}` in `{self.base_url}`')
        return self.session.put(self._build_url('pipeline', name))

    def update_pipeline(self, pipeline_id: str, pipeline_config: dict):
        self.logger.info(f'Update pipeline `{pipeline_id}` in `{self.base_url}`')
        return self.session.post(self._build_url('pipeline', pipeline_id), json=pipeline_config)

    def start_pipeline(self, pipeline_id: str):
        self.logger.info(f'Start pipeline `{pipeline_id}`')
        return self.session.post(self._build_url('pipeline', pipeline_id, 'start'), json={})

    def stop_pipeline(self, pipeline_id: str):
        self.logger.info(f'Stop pipeline `{pipeline_id}`')
        return self.session.post(self._build_url('pipeline', pipeline_id, 'stop'))

    def force_stop(self, pipeline_id: str):
        self.logger.info(f'Force stop pipeline `{pipeline_id}`')
        return self.session.post(self._build_url('pipeline', pipeline_id, 'forceStop'))

    def get_pipelines(self, order_by='NAME', order='ASC', label=None):
        self.logger.info('Get pipelines')
        params = {'orderBy': order_by, 'order': order}
        if label:
            params['label'] = label
        return self.session.get(self._build_url('pipelines'), params=params)

    def get_pipeline_statuses(self):
        self.logger.info('Get pipeline statuses')
        return self.session.get(self._build_url('pipelines', 'status'))

    def delete_pipeline(self, pipeline_id: str):
        self.logger.info(f'Delete pipeline `{pipeline_id}` from `{self.base_url}`')
        return self.session.delete(self._build_url('pipeline', pipeline_id))

    def get_pipeline_logs(self, pipeline_id: str, severity: str = None):
        self.logger.info(f'Get pipeline logs: `{pipeline_id}`, logging severity:{severity}')
        params = {'pipeline': pipeline_id, 'endingOffset': -1}
        if severity:
            params['severity.value'] = severity
        return self.session.get(self._build_url('system', 'logs'), params=params)

    def get_pipeline(self, pipeline_id: str):
        self.logger.info(f'Get pipeline `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id))

    def get_pipeline_status(self, pipeline_id: str):
        self.logger.info(f'Get pipeline status `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'status'))

    def get_pipeline_history(self, pipeline_id: str):
        self.logger.info(f'Get pipeline history `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'history'))

    def get_pipeline_metrics(self, pipeline_id: str):
        self.logger.info(f'Get pipeline metrics `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'metrics'))

    def reset_pipeline(self, pipeline_id: str):
        self.logger.info(f'Reset pipeline `{pipeline_id}`')
        return self.session.post(self._build_url('pipeline', pipeline_id, 'resetOffset'))

    def get_pipeline_offset(self, pipeline_id: str):
        return self.session.get(self._build_url('pipeline', pipeline_id, 'committedOffsets'))

    def post_pipeline_offset(self, pipeline_id: str, offset: dict):
        return self.session.post(self._build_url('pipeline', pipeline_id, 'committedOffsets'), json=offset)

    def validate(self, pipeline_id: str):
        self.logger.info(f'Validate pipeline `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'validate'),
                                params={'timeout': PREVIEW_TIMEOUT})

    def create_preview(self, pipeline_id: str):
        self.logger.info(f'Create pipeline `{pipeline_id}` preview')
        return self.session.post(self._build_url('pipeline', pipeline_id, 'preview'),
                                 params={'timeout': PREVIEW_TIMEOUT})

    def get_preview(self, pipeline_id: str, previewer_id: str):
        self.logger.info(f'Get preview `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'preview', previewer_id))

    def get_preview_status(self, pipeline_id: str, previewer_id: str):
        self.logger.info(f'Get preview status `{pipeline_id}`')
        return self.session.get(self._build_url('pipeline', pipeline_id, 'preview', previewer_id, 'status'))

    def get_jmx(self, query: str):
        return self.session.get(self._build_url('system', 'jmx'), params={'qry': query})

    def get_pipeline_errors(self, pipeline_id: str, stage_name):
        self.logger.info(f'Get pipeline `{pipeline_id}` errors')
        return self.session.get(
            self._build_url('pipeline', pipeline_id, 'errorRecords'),
            params={'stageInstanceName': stage_name}
        )


class ApiClientException(Exception):
    def __init__(self, message: str, exception_type: str = ''):
        self.exception_type = exception_type
        self.message = message

    @staticmethod
    def raise_from_response(response: dict):
        raise ApiClientException(
            response['RemoteException']['message'],
            response['RemoteException']['exception'],
        )


class UnauthorizedException(Exception):
    def __init__(self, message: str):
        self.message = message
        self.exception_type = ''


class PipelineFreezeException(Exception):
    pass
