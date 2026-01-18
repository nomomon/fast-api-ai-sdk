# FAst API & AI SDK template project

I noticed that there is a surge of requests for LLM chat wrapper projects. Having working on a few, I felt like they get quite repetitive. Some, stuff that needed to be setup required some thinking in terms of how to desing it properly. Going through a lot of refactoring, from one project to another, I decided its best maybe to set up a template project, with latest best practices, that I could reuse for future projects.

This project is developed as a monorepo using turborepo: frontend (Next.js) + backend (FastAPI). Working with Next.Js frontend and AI sdk, I realized how nice it is to have because it abstracts and simplifies a lot of ai handling stuff. However, I am not a big fan of having a node js backend. Shared code and types was nice, but it felt super cluttered and made me have to do a lot of mental gymnatics to figure out what's running on client and server.

In addition, I feel quite comfortable with using python and FastAPI for backend services. Python is also nice because it's really straight forward to add libraries and experiment with stuff.

Cost of integrating with AI SDK tho, is to handle streaming ourselves. But turns out it's not hard at all. There is an [example repo](https://github.com/vercel-labs/ai-sdk-preview-python-streaming) on how to do this.

In addition, for the frontend, I just started from another template repo, to [ai gateway demo](https://github.com/vercel-labs/ai-sdk-gateway-demo). It had a nice simple UI, with all the basics fronend setup already.
