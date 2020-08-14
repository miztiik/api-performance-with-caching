#!/usr/bin/env python3

from aws_cdk import core

from api_performance_with_caching.stacks.back_end.uncached_api_stack import UncachedApiStack
from api_performance_with_caching.stacks.back_end.cached_api_stack import CachedApiStack


app = core.App()
# API Best Practice Demonstration - Cached-vs-UnCached APIs. This stack deploy the backend datastore for both the API
# API Best Practice Demonstration - Cached-vs-UnCached APIs. This stack deploy the uncached API
uncached_api_stack = UncachedApiStack(
    app,
    "uncached-api",
    stack_log_level="INFO",
    back_end_api_name="uncached_api_01",
    back_end_api_datastore_name="uncached_api_01_datastore",
    description="Miztiik Automation: API Best Practice Demonstration. Cached-vs-UnCached APIs. This stack deploy the uncached API"
)

# API Best Practice Demonstration - Cached-vs-UnCached APIs. This stack deploy the cached API
cached_api_stack = CachedApiStack(
    app,
    "cached-api",
    stack_log_level="INFO",
    back_end_api_name="cached_api_01",
    back_end_api_datastore_name="cached_api_01_datastore",
    description="Miztiik Automation: API Best Practice Demonstration. Cached-vs-UnCached APIs. This stack deploy the cached API"
)


# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context('udemy_profile'))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context('skill_profile'))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context('about_me'))

app.synth()
