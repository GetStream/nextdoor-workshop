### Step 1 - Tutorial

Make sure to follow the React tutorial [here.](https://getstream.io/chat/react-chat/tutorial/)

### Step 2 - Auth integration

Once Stream Chat with the hardcoded auth and test data works well, we need to switch to proper authentication.
This way we can post messages from the React application using the same Next Door user that's logged in.

**Retrieve token from backend**

```typescript
import { TokenProvider } from 'stream-chat';

const createTokenProvider = (userId: string): TokenProvider => {
  return async function tokenProvider() {
    const response = await fetch('https://flask.gtstrm.com/generate-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
    });

    const { token } = await response.json();

    return token;
  };
};
```

**Connect using token provider**

```typescript
import { StreamChat } from 'stream-chat';

// this is the API key used for the workshop/staging app
const apiKey = 'b223hbsbgrpg';
// userId here is the Next Door user ID
const userId = 'REPLACE_WITH_NEXT_DOOR_USER_ID';

const client = new StreamChat(apiKey);
await client.connectUser(
  {
    id: userId,
  },
  createTokenProvider(userId),
);
```

### Useful links

- React SDK source code: https://github.com/GetStream/stream-chat-react
- Shared JS SDK source code: https://github.com/GetStream/stream-chat-js
- UI components docs: https://getstream.io/chat/docs/sdk/react/
- Low-level integration docs: https://getstream.io/chat/docs/react/
