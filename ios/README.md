### Step 1 - Tutorial

Make sure to follow the iOS tutorial (UIKIt) [here](https://getstream.io/tutorials/ios-chat/)

For now you do not need to complete each step of the tutorial, we can stop once we have the channel list `ViewController` working well.

### Step 2 - Auth integration

Once Stream Chat with the hardcoded auth and test data works well, we need to switch to proper authentication. 
This way we can post messages from the iOS using the same Next Door user that's logged in.

**Retrieve token from backend**

```swift
struct TokenResponse: Codable {
    let token: String
}

func requestToken(userId: String, completion: @escaping (Result<Token, Error>) -> Void) {
    guard let url = URL(string: "https://flask.gtstrm.com/generate-token") else {
        completion(.failure(NSError(domain: "Invalid URL", code: -1, userInfo: nil)))
        return
    }

    let payload = ["user_id": userId]
    
    do {
        let jsonData = try JSONSerialization.data(withJSONObject: payload)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        // Set the timeout interval to 1 second
        request.timeoutInterval = 1.0
        
        let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data received", code: -1, userInfo: nil)))
                return
            }
            
            do {
                let response = try JSONDecoder().decode(TokenResponse.self, from: data)
                completion(.success(Token(stringLiteral: response.token)))
            } catch {
                completion(.failure(error))
            }
        }
        task.resume()
    } catch {
        completion(.failure(error))
    }
}
```

**Connect using token provider**

```swift
// this is the API key used for the workshop/staging app
let config = ChatClientConfig(apiKey: .init("b223hbsbgrpg"))

// userId here is the Next Door user ID
let userId = "REPLACE_WITH_NEXT_DOOR_USER_ID"

ChatClient.shared.connectUser(
    userInfo: UserInfo(
        id: userId,
    ),
    tokenProvider: { completion in
        requestToken(userId: userId) { result in
            switch result {
            case .success(let token):
                completion(.success(token))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
)
```

### Useful links

- iOS SDK source code https://github.com/GetStream/stream-chat-swift/
- UI components docs https://getstream.io/chat/docs/sdk/ios/
- Low-level integration docs https://getstream.io/chat/docs/ios-swift/?language=swift
