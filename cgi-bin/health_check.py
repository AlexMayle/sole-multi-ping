#!/usr/bin/env python
#
#  This script checks each collection of a SolR Cloud cluster using either the 
#  SolR CLI or HTTP calls. It is meant to be invoked by a swerver upon receiving
#  a request from an AWS load balancer. If all collections are healthy, this script
#  executes without status code 0 and the server returns 200 OK. If at least one
#  collection is not 'healthy', an exception wil be raised. This results in a 
#  status code other than 0 being returned, and the server will respond to the
#  load balancer's request with a 500 error code. 
#

from __future__ import print_function
import xml.etree.ElementTree as ET
import subprocess
import httplib

HEALTHCHECK_TEMPLATE = "sudo /opt/solr/bin/solr healthcheck -c %s -z 10.10.8.32:2181"
CORE_API_URL = "/solr/admin/cores?action=STATUS"
PING_API_URL_TEMPLATE = "/solr/%s/admin/ping"
SOLR_CONN = httplib.HTTPConnection("localhost:8983")
SOLR_COLLECTIONS = [
        "sitecore_marketing_asset_index_web",
        "sitecore_core_index_secondary",
        "sitecore_testing_index",
        "sitecore_suggested_test_index_secondary",
        "sitecore_marketingdefinitions_master_secondary",
        "social_messages_master_secondary",
        "sitecore_fxm_web_index",
        "sitecore_testing_index_secondary",
        "cfa_com_master_index",
        "sitecore_core_index",
        "sitecore_analytics_index_secondary",
        "sitecore_analytics_index",
        "sitecore_marketing_asset_index_master",
        "cfa_com_web_index_secondary",
        "sitecore_web_index",
        "sitecore_marketingdefinitions_web_secondary",
        "social_messages_web_secondary",
        "sitecore_fxm_master_index_secondary",
        "sitecore_suggested_test_index",
        "sitecore_marketingdefinitions_master",
        "sitecore_fxm_master_index",
        "sitecore_master_index",
        "sitecore_web_index_secondary",
        "cfa_com_master_index_secondary",
        "sitecore_master_index_secondary",
        "sitecore_marketing_asset_index_web_secondary",
        "sitecore_fxm_web_index_secondary",
        "sitecore_list_index_secondary",
        "cfa_com_web_index",
        "sitecore_marketing_asset_index_master_secondary",
        "social_messages_master",
        "sitecore_list_index",
        "social_messages_web"
]

SOLR_CORES = [
	"cfa_com_master_index_secondary_shard1_replica1",
	"cfa_com_master_index_shard1_replica2",
	"cfa_com_web_index_secondary_shard1_replica2",
	"cfa_com_web_index_shard1_replica2",
	"sitecore_analytics_index_secondary_shard1_replica2",
	"sitecore_analytics_index_shard1_replica1",
	"sitecore_core_index_secondary_shard1_replica1",
	"sitecore_core_index_shard1_replica2",
	"sitecore_fxm_master_index_secondary_shard1_replica1",
	"sitecore_fxm_master_index_shard1_replica2",
	"sitecore_fxm_web_index_secondary_shard1_replica1",
	"sitecore_fxm_web_index_shard1_replica1",
	"sitecore_list_index_secondary_shard1_replica1",
	"sitecore_list_index_shard1_replica1",
	"sitecore_marketing_asset_index_master_secondary_shard1_replica2",
	"sitecore_marketing_asset_index_master_shard1_replica2",
	"sitecore_marketing_asset_index_web_secondary_shard1_replica1",
	"sitecore_marketing_asset_index_web_shard1_replica2",
	"sitecore_marketingdefinitions_master_secondary_shard1_replica2",
	"sitecore_marketingdefinitions_master_shard1_replica2",
	"sitecore_marketingdefinitions_web_secondary_shard1_replica1",
	"sitecore_marketingdefinitions_web_shard1_replica2",
	"sitecore_master_index_secondary_shard1_replica1",
	"sitecore_master_index_shard1_replica2",
	"sitecore_suggested_test_index_secondary_shard1_replica2",
	"sitecore_suggested_test_index_shard1_replica1",
	"sitecore_testing_index_secondary_shard1_replica1",
	"sitecore_testing_index_shard1_replica1",
	"sitecore_web_index_secondary_shard1_replica1",
	"sitecore_web_index_shard1_replica1",
	"social_messages_master_secondary_shard1_replica1",
	"social_messages_master_shard1_replica1",
	"social_messages_web_secondary_shard1_replica2",
	"social_messages_web_shard1_replica2"
]

def get_cores():
        """Gets a list of core names from solr host"""
        SOLR_CONN.request("GET", CORE_API_URL)
        response = SOLR_CONN.getresponse()
        response = ET.fromstring(response.read())
        response = response[2]
        cores = [core.attrib['name'] for core in response]
        return cores

def http_check_collection(col):
	"""Checks health of a collection using SolR HTTP call"""
        SOLR_CONN.request("GET", PING_API_URL_TEMPLATE % col)
        response = SOLR_CONN.getresponse()
	debug = response.read()
        status = True if response.status == 200 else False
        if not status:
            print(debug)
        return status


def cli_check_collection(col):
	"""Checks health of a collection using SolR CLI"""
	output = subprocess.check_output([HEALTHCHECK_TEMPLATE % col], shell=True)
	status = output.splitlines()[2]
	status = True if "healthy" in status else False
        if not status:
            print(status)
	return status


#  This won't run as 'main' when executed by the server
#  if __name__ == "main":
is_healthy = True
for core in get_cores():
	is_healthy = http_check_collection(core)
	if not is_healthy:
	        raise Exception("Collection '%s' is not healthy" % core)

