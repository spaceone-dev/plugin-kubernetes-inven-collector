import os
import logging

from kubernetes import client
from spaceone.core.connector import BaseConnector
from kubernetes.config.kube_config import KubeConfigLoader

DEFAULT_SCHEMA = 'google_oauth_client_id'
_LOGGER = logging.getLogger(__name__)


class KubernetesConnector(BaseConnector):

    def __init__(self, **kwargs):
        """
        kwargs
            - schema
            - options
            - secret_data

        secret_data(dict)
            - type: ..
            - project_id: ...
            - token_uri: ...
            - ...
        """
        #_LOGGER.debug(f'start k8s connector')
        super().__init__(transaction=None, config=None)
        secret_data = kwargs.get('secret_data')

        # Configure API Client
        kube_config = self._get_kube_config(secret_data)
        #_LOGGER.debug(f'kube_config => {kube_config}')
        loader = KubeConfigLoader(
            config_dict=kube_config
        )

        configuration = client.Configuration()
        loader.load_and_set(configuration)
        config = client.ApiClient(configuration)
        self.client = client.CoreV1Api(config)

    def verify(self, **kwargs):
        if self.client is None:
            self.set_connect(**kwargs)

    @staticmethod
    def _get_kube_config(secret_data):
        """
        Returns kube-config style object from secret_data
        
        :param secret_data: 
        :return: kube_config  
        """
        return {
            "apiVersion": "v1",
            "clusters": [
                {
                    "cluster": {
                        "certificate-authority-data": secret_data.get('certificate_authority_data', ''),
                        "server": secret_data.get('server', '')
                    },
                    "name": secret_data.get('cluster_name', '')
                }
            ],
            "contexts": [
                {
                    "context": {
                        "cluster": secret_data.get('cluster_name', ''),
                        "user": secret_data.get('cluster_name', '')
                    },
                    "name": secret_data.get('cluster_name', '')
                }
            ],
            "current-context": secret_data.get('cluster_name', ''),
            "kind": "Config",
            "preferences": {},
            "users": [
                {
                    "name": secret_data.get('cluster_name', ''),
                    "user": {
                        "token": secret_data.get('token', '')
                    }
                }
            ]
        }