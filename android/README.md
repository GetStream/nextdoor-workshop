### Step 1 - Tutorial

Make sure to follow the Android tutorial (UI-Components) [here](https://getstream.io/tutorials/android-chat/)

### Step 2 - Auth integration

Once Stream Chat with the hardcoded auth and test data works well, we need to switch to proper authentication. 
This way we can post messages from the Android app using the same Next Door user that's logged in.

**Retrieve token from backend**

```kotlin
import android.util.Log
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

fun requestToken(userId: String): String {
    var httpConnection: HttpURLConnection? = null
    try {
        val url = URL("https://flask.gtstrm.com/generate-token")
        val connection = (url.openConnection() as HttpURLConnection).also {
            httpConnection = it

            it.requestMethod = "POST"
            it.setRequestProperty("Content-Type", "application/json")
            // Set the timeout interval to 1 second
            it.connectTimeout = 1000
            it.readTimeout = 1000
        }
        val payload = JSONObject().apply {
            put("user_id", userId)
        }
        connection.outputStream.bufferedWriter().use {
            it.write(payload.toString())
        }
        val responseCode = connection.responseCode
        if (responseCode != HttpURLConnection.HTTP_OK) {
            throw IOException("Http response code is not OK: $responseCode")
        }
        return connection.inputStream.bufferedReader().use {
            JSONObject(
                it.readLine()
            ).getString("token")
        }
    } catch (e: Throwable) {
        Log.e("TokenService", "[requestToken] failed: $e")
        return ""
    } finally {
        httpConnection?.disconnect()
    }
}
```

**Connect using token provider**

```kotlin
// this is the API key used for the workshop/staging app
val apiKey = 'b223hbsbgrpg';

val client = ChatClient.Builder(apiKey, applicationContext)
    .withPlugin(
        StreamOfflinePluginFactory(
          config = Config(),
          appContext = applicationContext,
        )
    )
    .build()


// userId here is the Next Door user ID
val userId = "REPLACE_WITH_NEXT_DOOR_USER_ID"

client.connectUser(
    user = User(
        id = userId,
    ),
    tokenProvider = object : TokenProvider {
        override fun loadToken(): String {
            return requestToken(userId = userId)
        }
    }
)
```

### Useful links

- Android SDK source code https://github.com/GetStream/stream-chat-android/
- UI components docs https://getstream.io/chat/docs/sdk/android/
- Low-level integration docs https://getstream.io/chat/docs/android/?language=kotlin&name=android
