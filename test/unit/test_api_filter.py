from datetime import datetime, timedelta
from unittest import TestCase
from mock import Mock

from curator import api as curator

class FilterBySpace(TestCase):
    def test_filter_by_space_param_check(self):
        client = Mock()
        # Testing for the omission of the disk_space param
        self.assertFalse(curator.filter_by_space(client, ["index1", "index2"]))
    def test_filter_by_space_all_indices_closed(self):
        client = Mock()
        ds = 100.0
        indices = ["index1", "index2"]
        client.cluster.state.return_value = {
            'metadata': {
                'indices' : {
                    'index1' : {
                        'state' : 'close'
                    },
                    'index2' : {
                        'state' : 'close'
                    },
                }
            }
        }
        self.assertEqual([], curator.filter_by_space(client, indices, disk_space=ds))
    def test_filter_by_space_no_deletions_positive(self):
        client = Mock()
        ds = 10.0
        indices = ["index1", "index2"]
        client.cluster.state.return_value = {
            'metadata': {
                'indices' : {
                    'index1' : {
                        'state' : 'open'
                    },
                    'index2' : {
                        'state' : 'open'
                    },
                }
            }
        }
        # Build return value of over 1G in size for each index
        client.indices.status.return_value = {
            'indices' : {
                'index1' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
                'index2' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
            }
        }
        self.assertEqual([], curator.filter_by_space(client, indices, disk_space=ds))
    def test_filter_by_space_one_deletion(self):
        client = Mock()
        ds = 2.0
        indices = ["logstash-2015.02.25", "logstash-2015.02.26"]
        client.cluster.state.return_value = {
            'metadata': {
                'indices' : {
                    'logstash-2015.02.25' : {
                        'state' : 'open'
                    },
                    'logstash-2015.02.26' : {
                        'state' : 'open'
                    },
                }
            }
        }
        # Build return value of over 1G in size for each index
        client.indices.status.return_value = {
            'indices' : {
                'logstash-2015.02.25' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
                'logstash-2015.02.26' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
            }
        }
        self.assertEqual(["logstash-2015.02.25"], curator.filter_by_space(client, indices, disk_space=ds))
    def test_filter_by_space_one_deletion_no_reverse(self):
        client = Mock()
        ds = 2.0
        indices = ["index1", "index2"]
        client.cluster.state.return_value = {
            'metadata': {
                'indices' : {
                    'index1' : {
                        'state' : 'open'
                    },
                    'index2' : {
                        'state' : 'open'
                    },
                }
            }
        }
        # Build return value of over 1G in size for each index
        client.indices.status.return_value = {
            'indices' : {
                'index1' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
                'index2' : {
                    'index' : { 'primary_size_in_bytes': 1083741824 }
                },
            }
        }
        self.assertEqual(["index2"], curator.filter_by_space(client, indices, disk_space=ds, reverse=False))
