#!/usr/bin/env python3

from aws_cdk import core

from api_performance_with_caching.api_performance_with_caching_stack import ApiPerformanceWithCachingStack


app = core.App()
ApiPerformanceWithCachingStack(app, "api-performance-with-caching")

app.synth()
