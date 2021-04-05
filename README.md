# Shorten URL
  <h2>API</h2>
  <p>
    The API endpoints listed below are available.
  </p>
  <h2>FEATURES</h2>
  <p>
    <ul>
      <li>Faster with redis</li>
      <li>Ratelimit on api with Gloabl IP ban</li>
      <li>Light Weight & Easy to setup</li>
      <li>Heroku Supported</li>
    </ul>
  </p>
  <h2>INSTALLATION</h2>
  <p>
  <pre>
    <code>
      docker-compose up -d
    </code>
  </pre>
      Server will start in localhost:8000
  </p>
  
<!-- API:FIRST -->

  <h3>POST /create/times</h3>
  <p>
    Create a shorter URL with Access Limits.
  </p>
  <h4>Request</h4>
  <p>
    Parameters:
    <ul>
      <li>url – [str] full url</li>
      <li>times - [str, int] short code will be dead after TIMES visit</li>
    </ul>
  </p>
  <pre>
    <code>
      curl -X POST \
      --data '{"url": "https://google.com", "times": "3"}' \
      -H "Content-Type: application/json" {{ domain }}/create/times
    </code>
  </pre>
  <h4>Response</h4>
  <pre>
    <code>
      {"Auth":"7398e225-836e-4f60-9732-140cbf135e10","Code":"USTKUu","Created\
       At":"1616766726.4898272","Fullurl":"https://google.com","Times":"3"}
    </code>
  </pre>

<!-- API:END FIRST -->
<!-- API:SECOND -->

  <h3>POST /create/time</h3>
  <p>
    Create a shorter URL with time.
  </p>
  <h4>Request</h4>
  <p>
    Parameters:
    <ul>
      <li>url – [str] full url</li>
      <li>time - [str, int] short code will be dead after TIME seconds</li>
    </ul>
  </p>
  <pre>
    <code>
      curl -X POST \
      --data '{"url": "https://google.com", "time": "3"}' \
      -H "Content-Type: application/json" {{ domain }}/create/time
    </code>
  </pre>
  <h4>Response</h4>
  <pre>
    <code>
      {"Auth":"4f160d63-5ae2-4e28-a493-9c0e6b838768","Code":"vEXdWW","Created \
      At":"1616767277.039384","Fullurl":"https://google.com","Ttl In Seconds":"3"}
    </code>
  </pre>

<!-- API:END SECOND -->
<!-- API:THIRD -->

  <h3>DELETE /delete</h3>
  <p>
    Delete create url.
  </p>
  <h4>Request</h4>
  <p>
    Parameters:
    <ul>
      <li>code – [str] shorte code</li>
      <li>auth - [str] auth key of shorte code</li>
    </ul>
  </p>
  <pre>
    <code>
      curl -X DELETE \
      --data '{"code": "C0uSZg", "auth": "e56e03bc-8d11-40f7-bcf6-f1254af053a6"}' \
      -H "Content-Type: application/json" {{ domain }}/delete
    </code>
  </pre>
  <h4>Response</h4>
  <pre>
    <code>
      HTTP Status 204 (No Content)
    </code>
  </pre>

<!-- API:END THIRD -->
<!-- API:FOURTH -->

  <h3>POST /stats</h3>
  <p>
    Check your URL stats.
  </p>
  <h4>Request</h4>
  <p>
    Parameters:
    <ul>
      <li>code – [str] shorte code</li>
      <li>auth - [str] auth key of shorte code</li>
    </ul>
  </p>
  <pre>
    <code>
      curl -X POST \
      --data '{"code": "MK9qiH", "auth": "78afb120-6ab1-4f7f-a3ce-bce8e7a65693"}' \
      -H "Content-Type: application/json" {{ domain }}/stats
    </code>
  </pre>
  <h4>Response</h4>
  <pre>
    <code>
      {"Access":"1","Auth":"78afb120-6ab1-4f7f-a3ce-bce8e7a65693","Code":"MK9qiH","Created \
      At":"1616767969.7141504","Fullurl":"https://google.com","Last Visit":"1616768016.03026","Times":"2"}
    </code>
  </pre>

<!-- API:END FOURTH -->
  <h2>HTTP RESPONSE</h2>
  <pre>
    <code>
      CODE                      MEANING
      ======================================================================================================
      200 (OK)                  The request completed successfully.
      204 (NO CONTENT)          The request completed successfully but returned no content.
      401 (UNAUTHORIZED)        The Authorization header was missing or invalid.
      403 (FORBIDDEN)           The Authorization token you passed did not have permission to the resource.
      404 (NOT FOUND)           The resource at the location specified doesn't exist.
      405 (METHOD NOT ALLOWED)  The HTTP method used is not valid for the location specified.
      429 (TOO MANY REQUESTS)   You are being rate limited, see Rate Limits.
      5xx (SERVER ERROR)        The server had an error processing your request (these are rare).
    </code>
  </pre>

  <h2>SERVER RESPONSE</h2>
  <pre>
    <code>
      CODE    MEANING
      ==============================
      5000    SUCCESS
      5001    INVALID_DATA
      5002    RATE_LIMIT
      5003    NOT_FOUND
      5004    INVALID_URL
      5007    BLOCKED_IP
      5008    INVALID_SHORT_CODE
      5009    AUTH_FAILED
    </code>
  </pre>
