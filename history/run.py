#!/usr/bin/python
import utils
query = """
SELECT  payload_pull_request_head_repo_clone_url 
FROM [githubarchive:github.timeline]
WHERE payload_pull_request_base_user_login='{}'
GROUP BY payload_pull_request_head_repo_clone_url;"""

sc = utils.SimpleClient()
for x in  sc.runSyncQuery(query.format('taylorotwell')):
	print x 



