# FastAPI & Database Interview Q&A

---
## Q: What is the difference between WSGI and ASGI?

WSGI (Web Server Gateway Interface) is the old standard for Python web apps, designed for synchronous requests. It only supports HTTP, so every request blocks the worker until it finishes. Frameworks like Flask and Django (traditionally) run on WSGI.

ASGI (Asynchronous Server Gateway Interface) is the modern replacement. It supports both synchronous and asynchronous requests, and it can handle multiple protocols like HTTP, WebSockets, and background tasks. It’s non-blocking, meaning thousands of concurrent requests can be handled using async/await.

👉 In short:

WSGI = sync-only, HTTP-only, older.

ASGI = async + sync, HTTP + WebSockets, modern.

---

## Q: What is the difference between async/await and multithreading?


Async/await is cooperative multitasking. Tasks voluntarily yield control when they’re waiting (e.g., for I/O). It’s single-threaded but can handle thousands of concurrent tasks efficiently.

Multithreading uses multiple OS threads. Threads can run in parallel, but in Python they’re limited by the Global Interpreter Lock (GIL) for CPU-bound work. Threads also have higher memory overhead.

👉 Use async for I/O-bound tasks (APIs, DB, file I/O).
👉 Use multithreading/multiprocessing for CPU-bound tasks (image processing, ML training).

## What is Dependency Injection, and how is it implemented in FastAPI?

Dependency Injection (DI) is a design pattern where dependencies are not created inside a class or function but are provided externally. This makes code more modular, testable, and reusable.

In FastAPI, DI is implemented using the Depends function.

  - You define a function that provides the dependency (e.g., a DB session).

  - FastAPI automatically calls this function and injects the result into any route or dependency that declares it.
There are three main types of Dependency Injection:

    - Constructor Injection (dependencies passed at object creation),

    - Setter Injection (dependencies passed via setters/properties), and

    -Method Injection (dependencies passed as function/method arguments).
            FastAPI primarily uses Method Injection with its Depends system, making dependencies explicit, testable, and easy to manage.

## In FastAPI, if we declare the same dependency multiple times inside a single function, does FastAPI create it every time or reuse it?

FastAPI has a built-in request-scoped dependency cache.

 - If the same dependency function is declared multiple times within a single request, FastAPI calls it only once and reuses the result wherever needed.

 - This avoids duplicate work — for example, a database session dependency will be created once and injected multiple times within the same request.

 - However, across different requests, a new instance will always be created to avoid data leakage between users.


## What does "yield control" mean?

In async programming, yielding control means:
👉 “I’m pausing here because I’m waiting (e.g., for a DB, API, or file). Instead of blocking, I’ll let the event loop go do other work until I’m ready to contin

Yielding control means that when an async function hits an await (like a DB query or API call), it pauses itself and gives control back to the event loop. This lets the server run other tasks instead of blocking. Once the awaited operation finishes, the event loop resumes that function where it left off.

---

Async in Python means non-blocking execution using async/await. Instead of waiting for slow I/O operations like database queries or API calls, the server can handle other requests in the meantime. For example, two async tasks that each take 3 seconds can finish in 3 seconds total, instead of 6 with synchronous code. This is the main reason FastAPI (ASGI-based) is much faster and more scalable than traditional WSGI frameworks like Flask or Django.

## Q: What role does Uvicorn play in FastAPI?

Uvicorn is a lightweight, high-performance ASGI server. It runs FastAPI (or any ASGI app) and handles the actual network communication.

It’s fast because it uses:

uvloop (a C-based event loop faster than Python’s asyncio loop).

httptools (a very fast HTTP parser).

So when you run:

uvicorn main:app --reload


Uvicorn is the server process that takes HTTP requests, passes them to FastAPI, and sends back responses.

👉 Think of Uvicorn as the “engine” that powers FastAPI.

---

## Q: What is Starlette, and how is it related to FastAPI?


Starlette is a lightweight ASGI framework for building async web applications. It provides the core features like:

Routing

Middleware

Request/Response cycle

WebSockets

Background tasks

FastAPI is actually built on top of Starlette. FastAPI adds extra features like automatic request validation, dependency injection, and documentation (Swagger/OpenAPI), but it relies on Starlette for the low-level ASGI functionality.

👉 In short: Starlette = core ASGI toolkit, FastAPI = Starlette + Pydantic + Docs.

---

## Q: If Django and Flask now support ASGI, why is FastAPI still faster?

Yes, Django (via Channels) and  Flask (v2.0+) can run on ASGI, but they are sync-first frameworks. Their ORM, middleware, and request cycle are still mostly synchronous, so async support is patched in.

FastAPI, on the other hand, was async-native from the beginning, built directly on Starlette and Uvicorn. That means everything — routing, middleware, DB support — integrates with async/await without wrappers. This makes FastAPI leaner, cleaner, and faster under high concurrency.

---

## Q: Can you explain the difference between sync and async ORM usage in Django vs FastAPI?


In Django, the ORM is synchronous — if you call the database from an async view, you must wrap it with sync_to_async, which just runs the query in a threadpool. That means your request is still blocking resources, only shifted to another thread.

In FastAPI, you can use SQLAlchemy’s async ORM directly, so queries are truly non-blocking. This lets the server process other requests while waiting for the database, which scales much better under heavy load.

---

## Q: How would you compare middleware and request handling in FastAPI vs Django?


Django middleware and request cycle were originally built sync-first. While Django added support for async views, a lot of middleware is still synchronous, so mixing async and sync can introduce overhead.

In contrast, FastAPI middleware and request handling are async by default. Everything integrates with Python’s async/await directly, so you don’t need wrappers or conversions. This makes FastAPI much leaner and more performant for building APIs.

---

## Q: How do database indexes work?

- An **index** is a data structure (usually a **B-tree**) that keeps column values sorted.  
- It allows the database to find rows in **O(log n)** time instead of scanning the whole table.  
- **Example:** finding a user by email in 1M rows →  
  - Without index = full scan.  
  - With index = jump directly.  
- **Trade-offs:**  
  - Faster reads.  
  - Slower writes (index must also be updated).  
  - Extra storage.  
- **Best practice:** index columns used often in **WHERE, JOIN, ORDER BY, GROUP BY**.  

---

## Q: Why do we use `SessionLocal`?

- `sessionmaker` is a **factory** for creating sessions with predefined settings.  
- Instead of writing `AsyncSession(engine)` every time, `SessionLocal()` gives a **ready-to-use session**.  
- Ensures all sessions share the same config (**engine, async mode, expire_on_commit, etc.**).  

---

## Q: Why one session per request?

- FastAPI handles many **concurrent requests**.  
- If sessions are shared across requests → race conditions, data conflicts, or stale objects.  
- Each request having its **own session** keeps things **isolated and safe**.  

---

## Q: What is the purpose of `get_db`?

- A **dependency function** that provides a session to routes.  
- Centralizes session management (**open → yield → close**).  
- Avoids repeating session-handling code in every route.  

---

## Q: Why `async with`?

- `SessionLocal()` returns an **AsyncSession**.  
- `async with` ensures the session is:  
  - Opened at start.  
  - Closed automatically (even if errors happen).  
- Prevents **connection leaks**.  

---

## Q: Why `yield` instead of `return`?

- `yield` makes `get_db` act like a **context manager**.  
- FastAPI treats it as:  
  - Code before `yield` → setup (open session).  
  - Value from `yield` → injected into route.  
  - Code after `yield` → teardown (close session).  
- With `return`, teardown wouldn’t run → **connections might stay open**.  


---
## Q: In SQLAlchemy, I understand that ForeignKey and relationship work together but serve different purposes. Would you like me  to explain how the ForeignKey enforces database integrity, while the relationship gives Python-side navigation?”

ForeignKey defines the actual database constraint — it enforces that a column in one table references a column in another. relationship, on the other hand, is only on the ORM side; it lets me navigate between objects in Python, like book.category or category.books. They complement each other: ForeignKey is required for DB integrity, relationship is for ORM convenience
   -  With ForeignKey → you get the id and must query manually.
   -  With relationship → you get the full object automatically, and can still access the ID (book.category_id) if needed.

---

## Q: Lazy Loading vs. Eager Loading in SQLAlchemy

In SQLAlchemy, relationships can load data lazily or eagerly. Lazy loading is the default: the related object is only fetched when I access it, which can lead to the N+1 problem if I loop through many objects. Eager loading (joinedload or subqueryload) fetches related data in advance, either via a JOIN or a bulk secondary query, which avoids N+1 queries. The choice depends on whether I usually need the related data right away.

---

## Q: What is the role of async/await in FastAPI?

🧠 Core Concept:
FastAPI is built on top of Starlette, which supports asynchronous request handling using async def endpoints.

In FastAPI, async def endpoints allow non-blocking request handling using Python's async/await syntax. This is especially useful for IO-bound operations like database queries, HTTP requests, or file access. When we use await, the function yields control to the event loop, allowing other tasks to run. This improves concurrency and performance, especially under high load.

---

##  Q: When should you use async def vs def in FastAPI? 

🧠 Tip:

Use async def for non-blocking IO operations.

Use def for CPU-bound or synchronous operations.

I use async def when the route handler is performing non-blocking IO operations, such as calling a database with an async driver like asyncpg, making async HTTP requests, or reading files asynchronously. I stick to def when the logic is CPU-bound or when the libraries I use don’t support async — like standard SQLAlchemy or some image processing libraries — to avoid misleading async usage that still blocks the event loop.

---

##  Q: What happens if you use async def with a blocking operation in FastAPI?

🧠 Risk:
Blocking operations in async def routes can block the entire event loop, defeating the purpose of async.

If a blocking operation, like a heavy CPU task or a synchronous DB call, is placed inside an async def function without using await or background execution, it will block the event loop. This can degrade performance by preventing other requests from being processed. That’s why I offload such tasks using run_in_executor, or move them to a background task or worker queue.

---

##  Q: How does FastAPI handle concurrency with async?

🧠 FastAPI is built on ASGI — it's naturally concurrent.


FastAPI leverages Python’s async capabilities and runs on ASGI servers like Uvicorn, which manage an event loop to handle multiple requests concurrently. When an async def endpoint uses await, it yields control back to the event loop, allowing FastAPI to handle other requests in the meantime. This enables FastAPI to process thousands of concurrent requests efficiently, especially when dealing with IO-bound workloads.

---

##  Q: Can I mix async and sync code in FastAPI?

🧠 Yes, but be careful.l


Yes, FastAPI supports both async def and def route handlers. You can mix them based on the nature of the operation. However, mixing them improperly — for example, calling blocking code inside async def — can block the event loop and reduce performance. I ensure that blocking code stays in sync functions or is offloaded properly when used in async contexts.

---

##  Q: How do you make a blocking function async-compatible in FastAPI?

🧠 Use asyncio.run_in_executor.


To make a blocking function compatible with an async endpoint, I use asyncio.get_event_loop().run_in_executor() to offload it to a thread or process. This ensures the event loop stays free and the FastAPI server remains responsive. For CPU-heavy workloads, I prefer ProcessPoolExecutor over threads to avoid the Global Interpreter Lock (GIL) limitations.

---

##  Q: Does FastAPI support WebSockets with async?

🧠 Yes!


Yes, FastAPI has built-in support for WebSockets, and it's fully async-compatible. I’ve used it for real-time features like chat systems or live dashboards. The WebSocket endpoints are defined using async def, and FastAPI handles the connection lifecycle efficiently through the event loop.

---

##  Q: What’s the difference between concurrency and parallelism in FastAPI context?

🧠 Important conceptual difference.


Concurrency in FastAPI refers to the ability to handle multiple requests at the same time using async IO — even if they don’t run simultaneously. Parallelism, on the other hand, refers to running multiple operations at the same time using multiple CPU cores, typically using multiprocessing. FastAPI handles concurrency natively with as    ync/await, and I use parallelism via ProcessPoolExecutor or task queues when needed for CPU-bound tasks.

---

##  Q: How does async DB access work in FastAPI?

🧠 Use async ORM or drivers.
 

I use async-compatible libraries like SQLModel with AsyncEngine, Databases, or Tortoise ORM to perform async database access in FastAPI. These libraries allow me to await queries, keeping the request non-blocking. It’s important to avoid using sync ORMs like SQLAlchemy (non-async) directly in async routes, as it can block the event loop.

---

##  Q: How can you benchmark the performance impact of async in FastAPI?

🧠 Real-world scenario + tools


To benchmark async performance, I use tools like locust, ab, or wrk to simulate concurrent load. I compare the throughput and response time of async endpoints vs sync ones under similar conditions. I also profile the application using tools like py-spy or async-profiler to spot blocking operations or event loop delays.

---

##  Q: Why do we use JWT instead of sessions, cookies, or basic auth in FastAPI?
    
🧠 Stateless, scalable authentication


In FastAPI and modern API development, JWT is often preferred over sessions, cookies, or basic authentication because of its stateless nature and scalability.

Unlike session-based authentication, where the server stores user state, JWT embeds the user information directly in the token, which makes the authentication stateless and allows APIs to scale more easily across multiple servers or containers without shared session storage.

Compared to cookies, JWTs are typically sent in headers, which makes them more suitable for REST APIs and mobile or single-page applications, and they avoid some cross-origin limitations of cookies.

Basic authentication sends the username and password with every request, which is insecure and inefficient unless combined with HTTPS and additional mechanisms like token rotation.

JWTs also support short expiration times and refresh tokens, which allows better control over session lifetime and security. In FastAPI, this fits well with dependency injection and tools like OAuth2PasswordBearer, making JWT a very natural a0nd secure choice for API authentication.

---

##  Q: How do you handle CPU-bound tasks in FastAPI?

🧠 Offload CPU-intensive work


FastAPI is built on async IO and is great for handling concurrent IO-bound tasks, but for CPU-bound operations — like data processing or image manipulation — we need to ensure these don't block the event loop.

To handle this, I use run_in_executor() to offload CPU-heavy tasks to a separate thread or process. For more intensive or long-running jobs, I integrate a task queue like Celery to run them in the background asynchronously. This ensures the FastAPI app remains responsive and scalable.


In FastAPI, I can handle multiple requests efficiently by using async endpoints. When I define a route with async def and use await with non-blocking operations like asyncio.sleep, FastAPI uses the event loop to process multiple requests at the same time.

For example, if two clients call an async endpoint that sleeps for 3 seconds, they’ll both return around the same time. But if I use blocking code, like time.sleep(), inside a route, it blocks the event loop, and other requests are delayed. That’s why I either use proper async libraries or offload blocking work using run_in_executor() or background tasks.

---

##  Q: Why are coroutines important in FastAPI?

FastAPI uses async coroutines to handle multiple requests concurrently. When I define a route with async def, it becomes a coroutine. If I use await inside it — like when waiting for a database call — the coroutine yields control, and the event loop can start working on other coroutines. This lets FastAPI handle many requests at the same time, even in a single process.


Python uses reference counting for most memory management, but since reference counting cannot reclaim cyclic references, CPython adds a generational garbage collector.
Objects are grouped into 3 generations, with younger objects collected more frequently. The GC runs automatically when thresholds are crossed, but developers can control or force it using the gc module

In Python, the garbage collector’s job is to find and clean up reference cycles (objects that reference each other but are unreachable). Normal memory cleanup is handled by reference counting, while the GC supplements it to prevent memory leaks.