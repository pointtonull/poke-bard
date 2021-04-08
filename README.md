# poke-bard

API Requirements

- Retrieve Shakespearean description:

`GET endpoint: /pokemon/<pokemon name>`

Usage example (using httpie):

`http http://localhost:5000/pokemon/charizard`

Output format:

``` json
{
    "name": "charizard",
    "description": "Charizard flies 'round the sky in search of powerful
    opponents. 't breathes fire of such most wondrous heat yond 't melts aught.
    However, 't nev'r turns its fiery breath on any opponent weaker than itself."
}
```

Guidelines:
- Feel free to use any programming language, framework and library you want;
- Make it concise, readable and correct;
- Write automated tests for it!
- The task itself is trivial to keep it contained - we are interested to see how you work and
structure a project. Imagine this was a production feature;
- Useful APIs:
    - Shakespeare translator: https://funtranslations.com/api/shakespeare
    - PokéAPI: https://pokeapi.co/

Please describe in README.md:
- How to run it (don't assume anything already installed)
- Any areas you’re not happy with, and what improvements you’d make given more time

Bonus points for:
- Dockerfile;
- Include your Git history.

Have fun, take your time and when you are done please send a link to your
public Github repo to the talent partner you are in contact with.

Serverless using FastAPI / Magnum / Lambda and API Gateway.

The included Makefile abstracts the common development, testing, packaging, and
deploying steps.

- Builds the compiled zip artefact.  Upload zip artefact to S3.  Deploys lambda
- pointing to this source code.

It's ready to split the dependencies into layers, but I find it an unnecessary
complexity for this project.

Using SAM to keep it simple. It has the same capabilities as full-fledged
CloudFormation, but it's better suited for Serverless applications.

FastAPI is a very fast and elegant API Framework that offers OpenAPI
documentation, and good parallel processing support.

FastAPI runs on top of Mangum library, which serves as a wrapper for ASGI APIs
running inside of AWS Lambda and API Gateway. It provides an adapter, which:

- routes requests made to the API Gateway to our Lambda function
- routes Lambda function responses back to the API Gateway

# Why is this architecture attractive?

It provides a completely serverless API infrastructure with many benefits:

All advantages of Python and the amazing FastAPI library combined with the
benefits of a serverless architecture scalability & no backend server to manage
— API Gateway will spin up as many Lambda functions as needed to handle all
requests made to our API very cost-effective, especially for smaller APIs that
may not yet get millions of requests performant: due to Lambda’s context reuse,
consecutive requests (within 15 minutes from a previous request) reuse the
frozen execution context, allowing to mitigate the cold start of a serverless
function if enabled, API Gateway caching allows further latency improvements
easy management of API keys API Gateway provides integration with Active
Directories and third-party auth providers such as “Login with Google/Amazon
account” via Cognito out of the box centralized logging of all API requests and
responses, as well as access logs via CloudWatch distributed tracing capability
by enabling X-Ray traces.


With the free tier, you get monthly (free) access to:

1 million API Gateway requests 1 million Lambda invocations with up to 3.2
million seconds of compute time per month

Apart from that, the prices may vary depending on your AWS region and your
number of requests (bulk discount), but they are in ranges of 1–4.25 dollars
per one million requests (at the time of writing). Lambda is priced based on
the number of invocations and how long your code is running, measured in
milliseconds. You can find out more here and here.

# OpenAPI

https://beecd8ws3g.execute-api.eu-west-1.amazonaws.com/dev/docs

# Environment variables

``` sh
export STAGE="dev"
export ARTEFACTS_BUCKET="shakespearean-apis"
```

It'll use the longest available description. I am well aware of incosistencies
in `sword` and `diamond` with cherries and HP; but this pokedex is just for
fun.

# Dockerfile

Creating a dockerfile for fastapi is trivial[template]. So, I decided to take
it an step further and deploy it using a serverless architecture.

https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker

# Cache

Using a lookup table based on DynamoDB with TTL.
