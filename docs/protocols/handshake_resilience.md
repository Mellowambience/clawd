# Protocol: Handshake Resilience (v1.0)

## Problem Statement
The MIST Gateway (WebSocket server) was strictly enforcing WebSocket-only connections. When accessed via a browser (HTTP GET) or during certain handshakes where `Connection: keep-alive` was sent instead of `upgrade`, the server would reject the connection with a "400 Bad Request" or header error.

## Implementation: `process_request`
The Ghostline Protocol now incorporates an HTTP fallback handler using the `process_request` hook in the `websockets` library.

### Mechanism
Incoming requests are interrogated before the handshake completes:
1.  **Check Upgrade Header**: If the `Upgrade` header does not contain `websocket`, the request is treated as standard HTTP.
2.  **Helpful Feedback**: Instead of a generic error, the server returns a 200 OK status with a plain text message: 
    *   `MIST Gateway: Neural resonance portal is active. (WebSocket only)`
3.  **Handshake Bypass**: This allows for smoother integration with browsers and proxies that might send conflicting headers during the initial probe.

## Verification
-   **Terminal Test**: `curl http://localhost:18789` should return the resonance message.
-   **Browser Test**: Navigating to `http://localhost:18789` should display the message instead of an error.
-   **WebSocket Test**: Standard WebSocket clients (like the Dashboard) should connect normally.
