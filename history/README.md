Collects data with historical information about interaction between developers.

githubarchive data is used with google bigquery:
```
SELECT repository_url, actor_attributes_login
FROM [githubarchive:github.timeline]
WHERE type IN ("PushEvent", "PullRequestEvent", "MemberEvent") AND actor_attributes_login in ({})
GROUP BY repository_url, actor_attributes_login
IGNORE CASE;
```

The results are written to `output_data/repo_name` as json:
```
{
	timestamp: "2014-07-11 20:53:10",
	repos: {username:[list of repos], ...},
	users: [list of users],
	matrix: [matrix]
}
```

where `matrix` is an array of arrays with information about how many times two developers happened to touch the same repo
