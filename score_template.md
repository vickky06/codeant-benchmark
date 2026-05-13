# CodeAnt PR 1 — Scoring Template

CodeAnt comments captured: 9
Total defect weight available: 20

Mark each defect: replace `VERDICT: ?` with CAUGHT, PARTIAL, or MISSED.

  CAUGHT  = full weight  (names file AND identifies the issue)
  PARTIAL = half weight  (touches file/region, misses the issue)
  MISSED  = 0            (no relevant comment)

---

## D1 — Security (weight 5)
File: `src/services/helper_services/cleanup_service.rs`
Defect: Hardcoded bearer token (TELEMETRY_TOKEN constant)

### Candidate 1 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['TELEMETRY_TOKEN', 'TELEMETRY_URL', 'Bearer', 'secret', 'credential', 'hardcoded', 'token', 'Authorization']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323186

```
**Suggestion:** A production bearer token is hardcoded in source code, which is a credential exposure risk and can be leaked via repository access, logs, or artifacts. Move this token to secure configuration (environment/secret manager) and load it at runtime. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Production bearer token exposed directly in source control.
- ❌ Compromise of repo grants access to telemetry credentials.
- ⚠️ Token reuse across environments increases blast radius.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Open `src/services/helper_services/cleanup_service.rs:12-16` and observe the telemetry
configuration constants, including `TELEMETRY_URL` at line 12 and `TELEMETRY_TOKEN` at
lines 14-15, where a bearer token literal `"Bearer
rxc_live_a8f3b2e9d1c4_telemetry_prod_2026"` is embedded directly in source.

2. Inspect the `cleanup_ports` implementation in the same file at
`cleanup_service.rs:131-160`, where after running `kill_ports.sh` the code constructs a
telemetry call using `Command::new("curl")` at line 153 and passes `"-H",
&format!("Authorization: {}", TELEMETRY_TOKEN)` at line 157, meaning the hardcoded token
is sent on every telemetry POST.

3. Note that `CleanupService::cleanup()` in `cleanup_service.rs:20-52` calls
`Self::cleanup_ports(ports).await` at lines 39-41 when `ActivityType.ports` is set;
`main()` in `src/main.rs:146-161` constructs `ActivityType::new(...
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 160
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323199

```
**Suggestion:** This adds a blocking external process call inside an async function, which can block Tokio worker threads under load and degrade throughput. Use async HTTP client telemetry (with timeout) instead of synchronous `Command::output()` in async code. [performance]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Cleanup telemetry blocks Tokio worker during shutdown.
- ⚠️ Long-running curl calls delay overall service teardown.
- ⚠️ Async runtime concurrency reduced by blocking subprocess.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the binary with the `run` command so `main()` in `src/main.rs:74-124` starts the
gRPC and WebSocket servers and, upon shutdown (Ctrl+C signal handled at
`main.rs:126-131`), proceeds to the cleanup block at `main.rs:146-161` where
`CleanupService::cleanup(activity).await?` is awaited.

2. In `CleanupService::cleanup()`
(`src/services/helper_services/cleanup_service.rs:20-52`), when `ActivityType.ports` is
`Some` (constructed in `main.rs:154-159` from `ports_service.get_all_ports()`), the method
calls `Self::cleanup_ports(ports).await` at `cleanup_service.rs:39-41`, entering the async
function `cleanup_ports` at lines 131-160.

3. Inside `cleanup_ports`, after running `kill_ports.sh` and logging success/failure
(`cleanup_service.rs:138-151`), the code issues a telemetry call by constructing
`Command::new("curl")` and calling `.output()` at lines 153-160, all within the
... [truncated]
```

### Candidate 4 (inline)
Path: `src/services/websocket/websocket_server.rs`  Line: 49
Keyword hits: ['secret']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323206

```
**Suggestion:** Logging full inbound WebSocket payloads writes user-submitted code/content directly to audit logs, which can leak sensitive data and secrets from requests. Log only metadata (request id, session id, size, hash) or redact payload contents before logging. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ User-submitted code and data logged in full plaintext.
- ❌ Secrets embedded in code leak into audit logs.
- ⚠️ Log retention increases duration of sensitive data exposure.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the application with the `run` command so `main()` in `src/main.rs:60-72` spawns
the WebSocket server via `run_websocket_server(&websocket_addr)` at line 69, and
`run_websocket_server()` in `src/services/websocket/websocket_server.rs:22-30` binds a
`TcpListener` and accepts incoming connections.

2. Connect a WebSocket client to the configured address and send a text message containing
user code and potentially sensitive data (e.g., API keys or secrets embedded in code); the
server loop at `websocket_server.rs:31-40` reads each message and matches
`Ok(tungstenite::Message::Text(input_text))` at lines 41-42.

3. For each such message, the handler logs the full raw payload by computing a timestamp
and executing `eprintln!("[AUDIT ts={}] full_payload={}", ts, input_text);` at
`websocket_server.rs:45-49`, before any sanitization is applied; only afterward does it
call `
... [truncated]
```

### Candidate 5 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['TELEMETRY_TOKEN', 'Bearer', 'secret', 'credential', 'hardcoded', 'token', 'Authorization']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232327587

```
**🔴 Architect Review — CRITICAL**

A live telemetry bearer token is hardcoded in source (TELEMETRY_TOKEN) and used directly as the Authorization header, creating an immediate credential exposure and making secret rotation require code changes.

**Suggestion:** Move the telemetry credential to a runtime secret/config source (environment variable or secret manager), reference it via configuration at runtime instead of embedding the bearer value in code, and rotate the exposed token.


[Fix in Cursor](https://app.codeant.ai/fix-in-ide?tool=cursor&prompt=This%20is%20an%20%2A%2AArchitect%20%2F%20Logical%20Review%2A%2A%20comment%20left%20during%20a%20code%20review.%20These%20reviews%20are%20first-class%2C%20important%20findings%20%E2%80%94%20not%20optional%20suggestions.%20Do%20NOT%20dismiss%20this%20as%20a%20%27big%20architectural%20change%27%20just%20because%20the%20title%20says%20architect%20review%3B%20most%20of%20these%20can%20be%20resolved%20with%20a%20small%2C%20localized%20fix%20once%20the%20intent%20is%20understood.%0A%0A%2A%2APath%3A%2A%2A%20src%2Fservices%2Fhelper_services%2Fcleanup_service.rs%0A%2A%2ALine%3A%2A%2A%2012%3A15%0A%2A%2AComment%3A%2A%2A%0A%09%2ACRITICAL%3A%20A%20live%20telemetry%20bearer%20token%20is%20hardcoded%20in%20source%20%28TELEMETRY_TOKEN%29%20and%20used%20directly%20as%20the%20Authorization%20header%2C%20creating%20an%20immediate%20credential%20exposure%20and%20making%20secret%20rotation%20require%20code%20changes.%0A%0AValidate%20the%20correctness%
... [truncated]
```

**VERDICT: ?**

---

## D2 — Observability (weight 3)
File: `src/services/websocket/websocket_server.rs`
Defect: Logging unredacted client payload in [AUDIT ts=...] line

### Candidate 1 (inline)
Path: `src/services/execution_services/executor_service.rs`  Line: 81
Keyword hits: ['AUDIT']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323179

```
**Suggestion:** Returning success with an empty string on container execution failure hides real runtime errors and prevents recovery logic from running. This makes failed executions look successful to callers and can silently drop user output. Propagate the error instead of converting it to an empty successful response. [logic error]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Failed container executions appear as successful to gRPC clients.
- ❌ Callers cannot trigger retry or error handling on failures.
- ⚠️ Audit/logging loses visibility into execution error conditions.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the gRPC server using `main()` in `src/main.rs:35-88`, which wires
`ExecutorService` into the gRPC runtime via
`Server::builder().add_service(CodeExecutorServer::new(execution_service))` at
`src/main.rs:133-135`.

2. Issue an `Execute` gRPC request from a client so that validation passes;
`ExecutorService::execute()` in
`src/services/execution_services/executor_service.rs:18-38` calls
`ValidationService::validate_request()` and on success invokes
`session_handler(valid_data).await`.

3. Ensure there is an existing session/container for the `(session_id, language)` pair (so
`get_session_image()` succeeds), causing `session_handler()` in
`src/services/execution_services/executor_service.rs:47-60` to enter the `Ok(image)`
branch and call `docker_manager::execute_code_in_existing_containe
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['leak']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323186

```
**Suggestion:** A production bearer token is hardcoded in source code, which is a credential exposure risk and can be leaked via repository access, logs, or artifacts. Move this token to secure configuration (environment/secret manager) and load it at runtime. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Production bearer token exposed directly in source control.
- ❌ Compromise of repo grants access to telemetry credentials.
- ⚠️ Token reuse across environments increases blast radius.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Open `src/services/helper_services/cleanup_service.rs:12-16` and observe the telemetry
configuration constants, including `TELEMETRY_URL` at line 12 and `TELEMETRY_TOKEN` at
lines 14-15, where a bearer token literal `"Bearer
rxc_live_a8f3b2e9d1c4_telemetry_prod_2026"` is embedded directly in source.

2. Inspect the `cleanup_ports` implementation in the same file at
`cleanup_service.rs:131-160`, where after running `kill_ports.sh` the code constructs a
telemetry call using `Command::new("curl")` at line 153 and passes `"-H",
&format!("Authorization: {}", TELEMETRY_TOKEN)` at line 157, meaning the hardcoded token
is sent on every telemetry POST.

3. Note that `CleanupService::cleanup()` in `cleanup_service.rs:20-52` calls
`Self::cleanup_ports(ports).await` at lines 39-41 when `ActivityType.ports` is set;
`main()` in `src/main.rs:146-161` constructs `ActivityType::new(...
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
Keyword hits: ['leak']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

### Candidate 4 (inline)
Path: `src/services/websocket/websocket_server.rs`  Line: 49
Keyword hits: ['AUDIT', 'full_payload', 'input_text', 'sensitive', 'redact', 'leak']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323206

```
**Suggestion:** Logging full inbound WebSocket payloads writes user-submitted code/content directly to audit logs, which can leak sensitive data and secrets from requests. Log only metadata (request id, session id, size, hash) or redact payload contents before logging. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ User-submitted code and data logged in full plaintext.
- ❌ Secrets embedded in code leak into audit logs.
- ⚠️ Log retention increases duration of sensitive data exposure.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the application with the `run` command so `main()` in `src/main.rs:60-72` spawns
the WebSocket server via `run_websocket_server(&websocket_addr)` at line 69, and
`run_websocket_server()` in `src/services/websocket/websocket_server.rs:22-30` binds a
`TcpListener` and accepts incoming connections.

2. Connect a WebSocket client to the configured address and send a text message containing
user code and potentially sensitive data (e.g., API keys or secrets embedded in code); the
server loop at `websocket_server.rs:31-40` reads each message and matches
`Ok(tungstenite::Message::Text(input_text))` at lines 41-42.

3. For each such message, the handler logs the full raw payload by computing a timestamp
and executing `eprintln!("[AUDIT ts={}] full_payload={}", ts, input_text);` at
`websocket_server.rs:45-49`, before any sanitization is applied; only afterward does it
call `
... [truncated]
```

**VERDICT: ?**

---

## D3 — Compatibility (weight 5)
File: `src/proto/executor.proto`
Defect: Field tag changed from 2 to 5 (wire-breaking)

### Candidate 1 (inline)
Path: `src/proto/executor.proto`  Line: 11
Keyword hits: ['tag', 'field number', 'wire', 'compat', 'backward', 'schema', 'proto']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323170

```
**Suggestion:** Renumbering an existing protobuf field changes the wire contract and breaks backward compatibility with clients still sending the old field number. Requests from older clients will decode with an empty code payload, causing validation/execution failures. Keep the original tag for existing fields and only use new tag numbers for truly new fields. [api mismatch]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ gRPC Execute RPC ignores older client code payloads.
- ⚠️ Validation logic may reject otherwise valid legacy requests.
- ⚠️ Existing clients see silent failures with empty execution output.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Observe the server-side gRPC API definition in `src/proto/executor.proto:9-13`, where
`ExecuteRequest` defines `string language = 1;`, `string stdin = 3;`, and the `code` field
is now declared as `string code = 5;` (line 11).

2. Inspect the generated Rust message type in `src/proto/executor.rs:4-8` (found via Grep
results), where `ExecuteRequest` still has `#[prost(string, tag = "1")] pub language` and
`#[prost(string, tag = "2")] pub code`, reflecting the pre-change wire layout with `code`
at tag 2.

3. Run the gRPC server (`main()` in `src/main.rs:35-88`), which exposes the
`CodeExecutor::Execute` RPC by adding `CodeExecutorServer::new(execution_service)` in
`main.rs:133-135`, and uses `ExecuteRequest` as the inbound message type.

4. Use a client compile
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/execution_services/executor_service.rs`  Line: 81
Keyword hits: ['wire']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323179

```
**Suggestion:** Returning success with an empty string on container execution failure hides real runtime errors and prevents recovery logic from running. This makes failed executions look successful to callers and can silently drop user output. Propagate the error instead of converting it to an empty successful response. [logic error]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Failed container executions appear as successful to gRPC clients.
- ❌ Callers cannot trigger retry or error handling on failures.
- ⚠️ Audit/logging loses visibility into execution error conditions.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the gRPC server using `main()` in `src/main.rs:35-88`, which wires
`ExecutorService` into the gRPC runtime via
`Server::builder().add_service(CodeExecutorServer::new(execution_service))` at
`src/main.rs:133-135`.

2. Issue an `Execute` gRPC request from a client so that validation passes;
`ExecutorService::execute()` in
`src/services/execution_services/executor_service.rs:18-38` calls
`ValidationService::validate_request()` and on success invokes
`session_handler(valid_data).await`.

3. Ensure there is an existing session/container for the `(session_id, language)` pair (so
`get_session_image()` succeeds), causing `session_handler()` in
`src/services/execution_services/executor_service.rs:47-60` to enter the `Ok(image)`
branch and call `docker_manager::execute_code_in_existing_containe
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
Keyword hits: ['tag']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

**VERDICT: ?**

---

## D4 — Resource (weight 3)
File: `src/services/all_session_services/session_management_service.rs`
Defect: Removed dup-key check; HashMap.insert silently overwrites

### Candidate 1 (inline)
Path: `src/services/execution_services/executor_service.rs`  Line: 81
Keyword hits: ['container']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323179

```
**Suggestion:** Returning success with an empty string on container execution failure hides real runtime errors and prevents recovery logic from running. This makes failed executions look successful to callers and can silently drop user output. Propagate the error instead of converting it to an empty successful response. [logic error]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Failed container executions appear as successful to gRPC clients.
- ❌ Callers cannot trigger retry or error handling on failures.
- ⚠️ Audit/logging loses visibility into execution error conditions.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the gRPC server using `main()` in `src/main.rs:35-88`, which wires
`ExecutorService` into the gRPC runtime via
`Server::builder().add_service(CodeExecutorServer::new(execution_service))` at
`src/main.rs:133-135`.

2. Issue an `Execute` gRPC request from a client so that validation passes;
`ExecutorService::execute()` in
`src/services/execution_services/executor_service.rs:18-38` calls
`ValidationService::validate_request()` and on success invokes
`session_handler(valid_data).await`.

3. Ensure there is an existing session/container for the `(session_id, language)` pair (so
`get_session_image()` succeeds), causing `session_handler()` in
`src/services/execution_services/executor_service.rs:47-60` to enter the `Ok(image)`
branch and call `docker_manager::execute_code_in_existing_containe
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['leak']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323186

```
**Suggestion:** A production bearer token is hardcoded in source code, which is a credential exposure risk and can be leaked via repository access, logs, or artifacts. Move this token to secure configuration (environment/secret manager) and load it at runtime. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Production bearer token exposed directly in source control.
- ❌ Compromise of repo grants access to telemetry credentials.
- ⚠️ Token reuse across environments increases blast radius.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Open `src/services/helper_services/cleanup_service.rs:12-16` and observe the telemetry
configuration constants, including `TELEMETRY_URL` at line 12 and `TELEMETRY_TOKEN` at
lines 14-15, where a bearer token literal `"Bearer
rxc_live_a8f3b2e9d1c4_telemetry_prod_2026"` is embedded directly in source.

2. Inspect the `cleanup_ports` implementation in the same file at
`cleanup_service.rs:131-160`, where after running `kill_ports.sh` the code constructs a
telemetry call using `Command::new("curl")` at line 153 and passes `"-H",
&format!("Authorization: {}", TELEMETRY_TOKEN)` at line 157, meaning the hardcoded token
is sent on every telemetry POST.

3. Note that `CleanupService::cleanup()` in `cleanup_service.rs:20-52` calls
`Self::cleanup_ports(ports).await` at lines 39-41 when `ActivityType.ports` is set;
`main()` in `src/main.rs:146-161` constructs `ActivityType::new(...
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
Keyword hits: ['leak', 'container']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

### Candidate 4 (inline)
Path: `src/services/websocket/websocket_server.rs`  Line: 49
Keyword hits: ['leak', 'container']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323206

```
**Suggestion:** Logging full inbound WebSocket payloads writes user-submitted code/content directly to audit logs, which can leak sensitive data and secrets from requests. Log only metadata (request id, session id, size, hash) or redact payload contents before logging. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ User-submitted code and data logged in full plaintext.
- ❌ Secrets embedded in code leak into audit logs.
- ⚠️ Log retention increases duration of sensitive data exposure.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the application with the `run` command so `main()` in `src/main.rs:60-72` spawns
the WebSocket server via `run_websocket_server(&websocket_addr)` at line 69, and
`run_websocket_server()` in `src/services/websocket/websocket_server.rs:22-30` binds a
`TcpListener` and accepts incoming connections.

2. Connect a WebSocket client to the configured address and send a text message containing
user code and potentially sensitive data (e.g., API keys or secrets embedded in code); the
server loop at `websocket_server.rs:31-40` reads each message and matches
`Ok(tungstenite::Message::Text(input_text))` at lines 41-42.

3. For each such message, the handler logs the full raw payload by computing a timestamp
and executing `eprintln!("[AUDIT ts={}] full_payload={}", ts, input_text);` at
`websocket_server.rs:45-49`, before any sanitization is applied; only afterward does it
call `
... [truncated]
```

**VERDICT: ?**

---

## D5 — Correctness (weight 2)
File: `src/services/execution_services/executor_service.rs`
Defect: Returns Ok(empty) instead of Err on container error

### Candidate 1 (inline)
Path: `src/proto/executor.proto`  Line: 11
Keyword hits: ['silent', 'empty']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323170

```
**Suggestion:** Renumbering an existing protobuf field changes the wire contract and breaks backward compatibility with clients still sending the old field number. Requests from older clients will decode with an empty code payload, causing validation/execution failures. Keep the original tag for existing fields and only use new tag numbers for truly new fields. [api mismatch]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ gRPC Execute RPC ignores older client code payloads.
- ⚠️ Validation logic may reject otherwise valid legacy requests.
- ⚠️ Existing clients see silent failures with empty execution output.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Observe the server-side gRPC API definition in `src/proto/executor.proto:9-13`, where
`ExecuteRequest` defines `string language = 1;`, `string stdin = 3;`, and the `code` field
is now declared as `string code = 5;` (line 11).

2. Inspect the generated Rust message type in `src/proto/executor.rs:4-8` (found via Grep
results), where `ExecuteRequest` still has `#[prost(string, tag = "1")] pub language` and
`#[prost(string, tag = "2")] pub code`, reflecting the pre-change wire layout with `code`
at tag 2.

3. Run the gRPC server (`main()` in `src/main.rs:35-88`), which exposes the
`CodeExecutor::Execute` RPC by adding `CodeExecutorServer::new(execution_service)` in
`main.rs:133-135`, and uses `ExecuteRequest` as the inbound message type.

4. Use a client compile
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/execution_services/executor_service.rs`  Line: 81
Keyword hits: ['Ok(String', 'silent', 'Err', 'empty']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323179

```
**Suggestion:** Returning success with an empty string on container execution failure hides real runtime errors and prevents recovery logic from running. This makes failed executions look successful to callers and can silently drop user output. Propagate the error instead of converting it to an empty successful response. [logic error]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Failed container executions appear as successful to gRPC clients.
- ❌ Callers cannot trigger retry or error handling on failures.
- ⚠️ Audit/logging loses visibility into execution error conditions.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the gRPC server using `main()` in `src/main.rs:35-88`, which wires
`ExecutorService` into the gRPC runtime via
`Server::builder().add_service(CodeExecutorServer::new(execution_service))` at
`src/main.rs:133-135`.

2. Issue an `Execute` gRPC request from a client so that validation passes;
`ExecutorService::execute()` in
`src/services/execution_services/executor_service.rs:18-38` calls
`ValidationService::validate_request()` and on success invokes
`session_handler(valid_data).await`.

3. Ensure there is an existing session/container for the `(session_id, language)` pair (so
`get_session_image()` succeeds), causing `session_handler()` in
`src/services/execution_services/executor_service.rs:47-60` to enter the `Ok(image)`
branch and call `docker_manager::execute_code_in_existing_containe
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
Keyword hits: ['Err']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

### Candidate 4 (inline)
Path: `src/services/websocket/websocket_server.rs`  Line: 49
Keyword hits: ['Err']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323206

```
**Suggestion:** Logging full inbound WebSocket payloads writes user-submitted code/content directly to audit logs, which can leak sensitive data and secrets from requests. Log only metadata (request id, session id, size, hash) or redact payload contents before logging. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ User-submitted code and data logged in full plaintext.
- ❌ Secrets embedded in code leak into audit logs.
- ⚠️ Log retention increases duration of sensitive data exposure.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the application with the `run` command so `main()` in `src/main.rs:60-72` spawns
the WebSocket server via `run_websocket_server(&websocket_addr)` at line 69, and
`run_websocket_server()` in `src/services/websocket/websocket_server.rs:22-30` binds a
`TcpListener` and accepts incoming connections.

2. Connect a WebSocket client to the configured address and send a text message containing
user code and potentially sensitive data (e.g., API keys or secrets embedded in code); the
server loop at `websocket_server.rs:31-40` reads each message and matches
`Ok(tungstenite::Message::Text(input_text))` at lines 41-42.

3. For each such message, the handler logs the full raw payload by computing a timestamp
and executing `eprintln!("[AUDIT ts={}] full_payload={}", ts, input_text);` at
`websocket_server.rs:45-49`, before any sanitization is applied; only afterward does it
call `
... [truncated]
```

**VERDICT: ?**

---

## D6 — Failure-handling (weight 2)
File: `src/services/helper_services/cleanup_service.rs`
Defect: force: true -> false in RemoveContainerOptions

### Candidate 1 (inline)
Path: `src/services/execution_services/executor_service.rs`  Line: 81
Keyword hits: ['running']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323179

```
**Suggestion:** Returning success with an empty string on container execution failure hides real runtime errors and prevents recovery logic from running. This makes failed executions look successful to callers and can silently drop user output. Propagate the error instead of converting it to an empty successful response. [logic error]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Failed container executions appear as successful to gRPC clients.
- ❌ Callers cannot trigger retry or error handling on failures.
- ⚠️ Audit/logging loses visibility into execution error conditions.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Start the gRPC server using `main()` in `src/main.rs:35-88`, which wires
`ExecutorService` into the gRPC runtime via
`Server::builder().add_service(CodeExecutorServer::new(execution_service))` at
`src/main.rs:133-135`.

2. Issue an `Execute` gRPC request from a client so that validation passes;
`ExecutorService::execute()` in
`src/services/execution_services/executor_service.rs:18-38` calls
`ValidationService::validate_request()` and on success invokes
`session_handler(valid_data).await`.

3. Ensure there is an existing session/container for the `(session_id, language)` pair (so
`get_session_image()` succeeds), causing `session_handler()` in
`src/services/execution_services/executor_service.rs:47-60` to enter the `Ok(image)`
branch and call `docker_manager::execute_code_in_existing_containe
... [truncated]
```

### Candidate 2 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['running', 'cleanup']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323186

```
**Suggestion:** A production bearer token is hardcoded in source code, which is a credential exposure risk and can be leaked via repository access, logs, or artifacts. Move this token to secure configuration (environment/secret manager) and load it at runtime. [security]

<details>
<summary><b>Severity Level:</b> Critical 🚨</summary>

```mdx
- ❌ Production bearer token exposed directly in source control.
- ❌ Compromise of repo grants access to telemetry credentials.
- ⚠️ Token reuse across environments increases blast radius.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Open `src/services/helper_services/cleanup_service.rs:12-16` and observe the telemetry
configuration constants, including `TELEMETRY_URL` at line 12 and `TELEMETRY_TOKEN` at
lines 14-15, where a bearer token literal `"Bearer
rxc_live_a8f3b2e9d1c4_telemetry_prod_2026"` is embedded directly in source.

2. Inspect the `cleanup_ports` implementation in the same file at
`cleanup_service.rs:131-160`, where after running `kill_ports.sh` the code constructs a
telemetry call using `Command::new("curl")` at line 153 and passes `"-H",
&format!("Authorization: {}", TELEMETRY_TOKEN)` at line 157, meaning the hardcoded token
is sent on every telemetry POST.

3. Note that `CleanupService::cleanup()` in `cleanup_service.rs:20-52` calls
`Self::cleanup_ports(ports).await` at lines 39-41 when `ActivityType.ports` is set;
`main()` in `src/main.rs:146-161` constructs `ActivityType::new(...
... [truncated]
```

### Candidate 3 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 85
Keyword hits: ['force', 'RemoveContainerOptions', 'running', 'cleanup']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323191

```
**Suggestion:** Container cleanup now uses non-forced removal, but this cleanup path iterates active containers; Docker will reject removing running containers without force, causing cleanup to fail and leaving stale resources behind. Either stop containers first or keep forced removal where this path expects guaranteed cleanup. [resource leak]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Labeled containers may remain running after shutdown.
- ⚠️ Cleanup failures bubble up and abort post-run teardown.
- ⚠️ Resource leakage over time increases operational footprint.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the main binary with the `run` command (e.g., `cargo run -- run`), causing `main()`
in `src/main.rs:35-84` to initialize config and then, after the gRPC and WebSocket servers
exit, execute the cleanup sequence starting at `src/main.rs:146-161` where
`CleanupService` is instantiated and `cleanup_service.cleanup(activity).await?` is
invoked.

2. Observe that `ActivityType::new(...)` in `src/main.rs:154-159` passes
`Some(container.to_string())` and `Some(all_tars.to_string())` plus
`Some(ports_service.get_all_ports())`, ensuring that `CleanupService::cleanup()` in
`src/services/helper_services/cleanup_service.rs:20-52` will call
`Self::cleanup_containers().await?` at lines 23-25.

3. In `cleanup_containers()` (`cleanup_service.rs:54-95`), the code enumerates all
containers via `docker.list_container
... [truncated]
```

### Candidate 4 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 160
Keyword hits: ['running', 'cleanup']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232323199

```
**Suggestion:** This adds a blocking external process call inside an async function, which can block Tokio worker threads under load and degrade throughput. Use async HTTP client telemetry (with timeout) instead of synchronous `Command::output()` in async code. [performance]

<details>
<summary><b>Severity Level:</b> Major ⚠️</summary>

```mdx
- ⚠️ Cleanup telemetry blocks Tokio worker during shutdown.
- ⚠️ Long-running curl calls delay overall service teardown.
- ⚠️ Async runtime concurrency reduced by blocking subprocess.
```
</details>
<details>
<summary><b>Steps of Reproduction ✅ </b></summary>

```mdx
1. Run the binary with the `run` command so `main()` in `src/main.rs:74-124` starts the
gRPC and WebSocket servers and, upon shutdown (Ctrl+C signal handled at
`main.rs:126-131`), proceeds to the cleanup block at `main.rs:146-161` where
`CleanupService::cleanup(activity).await?` is awaited.

2. In `CleanupService::cleanup()`
(`src/services/helper_services/cleanup_service.rs:20-52`), when `ActivityType.ports` is
`Some` (constructed in `main.rs:154-159` from `ports_service.get_all_ports()`), the method
calls `Self::cleanup_ports(ports).await` at `cleanup_service.rs:39-41`, entering the async
function `cleanup_ports` at lines 131-160.

3. Inside `cleanup_ports`, after running `kill_ports.sh` and logging success/failure
(`cleanup_service.rs:138-151`), the code issues a telemetry call by constructing
`Command::new("curl")` and calling `.output()` at lines 153-160, all within the
... [truncated]
```

### Candidate 5 (inline)
Path: `src/services/helper_services/cleanup_service.rs`  Line: 15
Keyword hits: ['cleanup']
URL: https://github.com/vickky06/Rexec/pull/7#discussion_r3232327587

```
**🔴 Architect Review — CRITICAL**

A live telemetry bearer token is hardcoded in source (TELEMETRY_TOKEN) and used directly as the Authorization header, creating an immediate credential exposure and making secret rotation require code changes.

**Suggestion:** Move the telemetry credential to a runtime secret/config source (environment variable or secret manager), reference it via configuration at runtime instead of embedding the bearer value in code, and rotate the exposed token.


[Fix in Cursor](https://app.codeant.ai/fix-in-ide?tool=cursor&prompt=This%20is%20an%20%2A%2AArchitect%20%2F%20Logical%20Review%2A%2A%20comment%20left%20during%20a%20code%20review.%20These%20reviews%20are%20first-class%2C%20important%20findings%20%E2%80%94%20not%20optional%20suggestions.%20Do%20NOT%20dismiss%20this%20as%20a%20%27big%20architectural%20change%27%20just%20because%20the%20title%20says%20architect%20review%3B%20most%20of%20these%20can%20be%20resolved%20with%20a%20small%2C%20localized%20fix%20once%20the%20intent%20is%20understood.%0A%0A%2A%2APath%3A%2A%2A%20src%2Fservices%2Fhelper_services%2Fcleanup_service.rs%0A%2A%2ALine%3A%2A%2A%2012%3A15%0A%2A%2AComment%3A%2A%2A%0A%09%2ACRITICAL%3A%20A%20live%20telemetry%20bearer%20token%20is%20hardcoded%20in%20source%20%28TELEMETRY_TOKEN%29%20and%20used%20directly%20as%20the%20Authorization%20header%2C%20creating%20an%20immediate%20credential%20exposure%20and%20making%20secret%20rotation%20require%20code%20changes.%0A%0AValidate%20the%20correctness%
... [truncated]
```

**VERDICT: ?**

---
