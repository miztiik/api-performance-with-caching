# API Best Practices: Highly Performant API Design

Mystique Unicorn App is a building new application based on microservice architectural pattern. The app provides updates on events in real-time. At any given time, there will be a number of users querying for the same data (Very much like match data of a sporting event). During the event, Mystique corp would like to keep the latency as low as possible and while maintaining the data freshness. Once the event is no longer relevant, the query load on the API will be siginificantly less and latency is not a concern. As an cloud consultant to Mystique Corp, can you help their dev team to maintain _lower latency_ and _data freshness_ of their app?

## 🎯Solutions

Ideally, an API request is RESTful, i.e. it makes use of HTTP semantics. Read requests are made using the GET method, authentication credentials are included via a header, and reads are broken down into small, atomic chunks. HTTP is designed to facilitate caching.

In-memory data caching can be one of the most effective strategies to improve your overall application performance and to reduce your database costs. By caching reusable data among requests, We can ensure the application running on the edge is able to maintain lower latency. Every cache requires local storage and content needs to be loaded into memory cache memory.

If the rate of change of the data is very high, then cache will become stale at the same rate. It is important to choose the appropriate cache invalidation strategies. Setting _Time-To-Live(TTL)_ is one common way of invalidation. With API Gateway caching, you can cache responses to any request, including POST, PUT and PATCH. _However, this is not enabled by default._

![API Best Practices: Highly Performant API Design](images/miztiik_api_caching_architecture_00.png)

In this article, we will build the above architecture. using Cloudformation generated using [AWS Cloud Development Kit (CDK)][102]. The architecture has been designed in a modular way so that we can build them individually and integrate them together. The prerequisites to build this architecture are listed below

1.  ## 🧰 Prerequisites

    This demo, instructions, scripts and cloudformation template is designed to be run in `us-east-1`. With few modifications you can try it out in other regions as well(_Not covered here_).

    - 🛠 AWS CLI Installed & Configured - [Get help here](https://youtu.be/TPyyfmQte0U)
    - 🛠 AWS CDK Installed & Configured - [Get help here](https://www.youtube.com/watch?v=MKwxpszw0Rc)
    - 🛠 Python Packages, _Change the below commands to suit your OS, the following is written for amzn linux 2_
      - Python3 - `yum install -y python3`
      - Python Pip - `yum install -y python-pip`
      - Virtualenv - `pip3 install virtualenv`

1.  ## ⚙️ Setting up the environment

    - Get the application code

      ```bash
      git clone https://github.com/miztiik/secure-api-with-throttling.git
      cd secure-api-with-throttling
      ```

1.  ## 🚀 Prepare the dev environment to run AWS CDK

    We will cdk to be installed to make our deployments easier. Lets go ahead and install the necessary components.

    ```bash
    # If you DONT have cdk installed
    npm install -g aws-cdk

    # Make sure you in root directory
    python3 -m venv .env
    source .env/bin/activate
    pip3 install -r requirements.txt
    ```

    The very first time you deploy an AWS CDK app into an environment _(account/region)_, you’ll need to install a `bootstrap stack`, Otherwise just go ahead and deploy using `cdk deploy`.

    ```bash
    cdk bootstrap
    cdk ls
    # Follow on screen prompts
    ```

    You should see an output of the available stacks,

    ```bash
    uncached-api
    cached-api
    ```

1.  ## 🚀 Deploying the application

    Let us walk through each of the stacks,

    - **Stack: uncached-api**
      We are going to deploy a simple api running as a lambda function. This API is deployed as public endpoint without any caching. When the api is invoked, The backend processess the request and does two things:

      - Returns an movie item data
      - Add the request processed timestamp to the response

      There are two api resources available for us,

      - `{UNCACHED_API_URL}` - Every invocation will return a random movie item data
      - `{UNCACHED_API_URL}/{id}` - As this is a sample, there are only _10_ movies in the database.You can also invoke query the database for a movie by providing an _id_. The _id_ value can be between `{0..9}`

      Initiate the deployment with the following command,

      ```bash
      cdk deploy uncached-api
      ```

      _Expected output:_
      The `UncachedApiUrl` can be found in the outputs section of the stack,

      ```bash
      $ UNCACHED_API_URL="https://x60fl6u8f7.execute-api.us-east-1.amazonaws.com/miztiik/uncached/movie"
      $ curl ${UNCACHED_API_URL}
        {
          "message": "Hello Miztiikal World, How is it going?",
          "movie": {
            "year": {
              "S": "2013"
            },
            "id": {
              "S": "3"
            },
            "title": {
              "S": "Thor: The Dark World"
            }
          },
          "ts": "2020-08-16 21:55:09.887050"
        }
      # Queryiing on movie id
      $ curl ${UNCACHED_API_URL}/9
        {
          "message": "Hello Miztiikal World, How is it going?",
          "movie": {
            "year": {
              "S": "2013"
            },
            "id": {
              "S": "9"
            },
            "rating": {
              "S": "7.3"
            },
            "title": {
              "S": "Now You See Me"
            }
          },
          "ts": "2020-08-16 21:53:49.432507"
        }
      ```

      As you make multiple queries to the API, You can observe that the timestamp changes for each invocation. This shows that each of the request invokes the backend lambda(_You can also check the lambda execution logs in cloudwatch._). We also can make a note of the latency for each of the request by prefixing our bash commands with `time` or using an utility like `Postman`.


      ```bash
      # Queryiing on movie id
      $ curl ${UNCACHED_API_URL}/9
      {
        "message": "Hello Miztiikal World, How is it going?",
        "movie": {
          "year": {
            "S": "2013"
          },
          "id": {
            "S": "9"
          },
          "rating": {
            "S": "7.3"
          },
          "title": {
            "S": "Now You See Me"
          }
        },
        "ts": "2020-08-16 22:13:24.994078"
      }
      real    0m1.482s
      user    0m0.025s
      sys     0m0.017s
      ```

      Here you can observe the latency varies between `300`ms to `1400`ms. This is what we want to avoid and optimize our api so that we can provide consisitent user experience.

    - **Stack: cached-api**

      This stack:_cached-api_ is very much similar to the previous stack. In addition to that, We will also add caching. To observe the benefit of caching, we will enable it on only one of the resources, this also demonstrats the ability of API Gateway to allow granular caching.

      - Caching **OFF**: `{CACHED_URL}` - When this url is invoked, we get a random movie item data, but the response is _not_ cached. Every request is passed onto the backend for processing
      - Caching **ON**: `{CACHED_URL}/{id}` - On invocation, returns the movie item for the given `{id}` and _caches_ the response. When an request for the same `{id}` comes along within the TTL the request is served from cache.

        - _Customizations_: You can change the `TTL` value and the cache size. In this demo,
          - `TTL` = 30Seconds
          - `Cache Size` = 0.5GB


          Try changing them to see how it impacts the performance of your API.

      Initiate the deployment with the following command,

      ```bash
      cdk deploy cached-api
      ```

      Check the `Outputs` section of the stack to access the `CachedApiUrl`

1.  ## 🔬 Testing the solution

    We can use a tool like `curl` or `Postman` to query the url and measure the response time

    We need a tool/utility to generate 100's or 1000's or requests simulating a real-world use case. We can use the community edition of the `artillery` for this purpose. We will build a VPC and host an EC2 instance that can run this tool. _Additional Activity, Do try this at home: Run artillery as a fargate task_

    The _Outputs_ section of the `secure-private-api` stack has the required information on the urls

    - We need to invoke the `SecureApiUrl` from the same VPC. To make it easier to test the solution, I have created another template that will deploy an EC2 instance in the same VPC and in the same security group as the API Gateway. You can login to the instances using [Systems Manager](https://www.youtube.com/watch?v=-ASMtZBrx-k). You can deploy this stack or create your own instance.

      Initiate the deployment with the following command,

      ```bash
      cdk deploy load-generator-vpc-stack
      cdk deploy miztiik-artillery-load-generator
      ```

    - Connect to the EC2 instance using Session Manager - [Get help here](https://www.youtube.com/watch?v=-ASMtZBrx-k)

      - Switch to bash shell `bash`
      - Install `nodejs`

        ```bash
        # https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
        . ~/.nvm/nvm.sh
        nvm install node
        # Confirm Node is installed properly
        node -e "console.log('Running Node.js ' + process.version)"
        # Install artilleruy
        npm install -g artillery
        # Setup log file location to save artillery test results
        sudo touch /var/log/miztiik-load-generator-unthrottled.log
        sudo touch /var/log/miztiik-load-generator-throttled.log
        sudo chown ssm-user:ssm-user /var/log/miztiik-load-generator-*
        ```

    Now we are all almost set to bombard our APIs with requests. As the first step, let us set our API url as environment variables. Ensure you change the values from the appropriate stack

    ```bash
    UNTHROTLLED_API_URL="https://3t354sxysj.execute-api.us-east-1.amazonaws.com/miztiik-unthrottled/unsecure/greeter"
    SECURE_API_URL="https://9r4ftbohse.execute-api.us-east-1.amazonaws.com/miztiik-throttled/secure/greeter"
    ```

    The below artillery request will generate about 1500 requests, simulating the arrival of 5 users per second and each generating one request. We have also informed artillery to add new users for about 5 minutes(_300 seconds_). In a real-world scenario, you might want to throw much bigger requests at your workloads. If you are testing and playaround with the services, this can be a good starting point.

    ```bash
     artillery quick -d 310 -r 5 -n 1 ${UNTHROTLLED_API_URL} >> /var/log/miztiik-load-generator-unthrottled.log &
     artillery quick -d 310 -r 5 -n 1 ${SECURE_API_URL} >> /var/log/miztiik-load-generator-throttled.log &

     # Check the logs for summary
     tail -20 /var/log/miztiik-load-generator-unthrottled.log
     tail -20 /var/log/miztiik-load-generator-throttled.log
    ```

    Expected Output,

    ```bash
    $ curl ${SECURE_API_URL}
    {"message":"Forbidden"}

    # If you want to try verbose curl
    $ curl -v ${SECURE_API_URL}
    # truncated output
    ...
    < HTTP/2 403
    < content-type: application/json
    < content-length: 23
    < x-amzn-requestid: b5b76376-29f1-4e9a-99e6-5e19ebe7bb82
    < x-amzn-errortype: ForbiddenException
    < x-cache: Error from cloudfront
    < via: 1.1 5eb5e19c1a78889d10ff8f1551ed2aa.cloudfront.net (CloudFront)
    < x-amz-cf-pop: IAD89-C1
    < x-amz-cf-id: MngW-1YE6-LXbV6d5K21jOtSYTkVdVd_IUDMAvk4HWUaYLVtxeRQA==
    ...
    # truncated output
    ```

    You can notice that after throwing more `133` requests at the WAF+API GW, You should be able to see the public IP address of EC2 instances being blocked by WAF. _Dont forget to update the \_web-acl-id_ of your waf

    ```bash
    curl -H "Cache-control: max-age=0" $API_ENDPOINT - This should print a timestamp that changes every second you run it, because the Cache-Control header is being respected despite the fact that requireAuthorizationForCacheControl is true. This is NOT expected
    ```

    ```bash
    CACHED_API_URL=""
    runtime=31
    now=$(date +%s)
    future=$((now+runtime))
    while [ $(date "+%s") -le $future ]
    do
    curl ${CACHED_API_URL}
    echo -e "=== `date +%s` ==="
    done
    ```


    Here is a snapshot of the WAF dashboard showing the `allowed` and `blocked` requests. As the requests reached the threshold in a `5` minute period, all the remaning requests were blocked.

    ![Security best practices in Amazon API Gateway: Throttling & Web Application Firewallm](images/miztiik_api_security_waf_00.png)


    You can observe here that, With throttling & WAF, we were able to block a significant amount of spam traffic, maintain the `min` response times under increased load and also serve a _p95_ in about `300ms`

    _Additional Learnings:_ You can check the logs in cloudwatch for more information or increase the logging level of the lambda functions by changing the environment variable from `INFO` to `DEBUG`

1.  ## 🧹 CleanUp

    If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

    - Resources created during [Deploying The Application](#deploying-the-application)
    - Delete CloudWatch Lambda LogGroups
    - _Any other custom resources, you have created for this demo_

    ```bash
    # Delete from cdk
    cdk destroy

    # Follow any on-screen prompts

    # Delete the CF Stack, If you used cloudformation to deploy the stack.
    aws cloudformation delete-stack \
        --stack-name "MiztiikAutomationStack" \
        --region "${AWS_REGION}"
    ```

    This is not an exhaustive list, please carry out other necessary steps as maybe applicable to your needs.

## 📌 Who is using this

This repository to teaches how to secure your api with WAF & API GW Throttling to new developers, Solution Architects & Ops Engineers in AWS. Based on that knowledge these Udemy [course #1][103], [course #2][102] helps you build complete architecture in AWS.

### 💡 Help/Suggestions or 🐛 Bugs

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional documentation or solutions, we greatly value feedback and contributions from our community. [Start here][200]

### 👋 Buy me a coffee

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q41QDGK)Buy me a [coffee ☕][900].

### 📚 References

1. [Throttle API requests for better throughput][1]

1. [Rate Based WAFv2 Rules][2]

1. [Troubleshoot HTTP 403 Forbidden errors from API Gateway][3]

1. [Update WebAcl to WAFv2][4]

1. [Protecting APIs using AWS WAF][5]

### 🏷️ Metadata

**Level**: 300

![miztiik-success-green](https://img.shields.io/badge/miztiik-success-green)

https://aws.amazon.com/premiumsupport/knowledge-center/best-practices-custom-cf-lambda/
https://aws.amazon.com/premiumsupport/knowledge-center/cloudformation-stack-delete-failed/
https://aws.amazon.com/premiumsupport/knowledge-center/cloudformation-lambda-resource-delete/
https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
https://d0.awsstatic.com/whitepapers/Database/database-caching-strategies-using-redis.pdf
https://forums.aws.amazon.com/thread.jspa?threadID=195290#646425

[1]: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html
[2]: https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html
[3]: https://aws.amazon.com/premiumsupport/knowledge-center/api-gateway-troubleshoot-403-forbidden/
[4]: https://docs.aws.amazon.com/waf/latest/APIReference/API_UpdateWebACL.html
[5]: https://aws.amazon.com/blogs/compute/protecting-your-api-using-amazon-api-gateway-and-aws-waf-part-i/
[100]: https://www.udemy.com/course/aws-cloud-security/?referralCode=B7F1B6C78B45ADAF77A9
[101]: https://www.udemy.com/course/aws-cloud-security-proactive-way/?referralCode=71DC542AD4481309A441
[102]: https://www.udemy.com/course/aws-cloud-development-kit-from-beginner-to-professional/?referralCode=E15D7FB64E417C547579
[103]: https://www.udemy.com/course/aws-cloudformation-basics?referralCode=93AD3B1530BC871093D6
[200]: https://github.com/miztiik/secure-api-with-throttling/issues
[899]: https://www.udemy.com/user/n-kumar/
[900]: https://ko-fi.com/miztiik
[901]: https://ko-fi.com/Q5Q41QDGK
