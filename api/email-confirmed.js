export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/html');
  res.status(200).send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Confirmed - HerFoodCode</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8fafc;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        .success-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        h1 {
            color: #059669;
            margin-bottom: 16px;
            font-size: 24px;
        }
        p {
            color: #6b7280;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        .button {
            background-color: #059669;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 8px;
        }
        .button:hover {
            background-color: #047857;
        }
        .button-secondary {
            background-color: transparent;
            color: #059669;
            border: 1px solid #059669;
        }
        .button-secondary:hover {
            background-color: #f0fdf4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Email Confirmed!</h1>
        <p>Your email has been successfully verified. You can now continue with your health journey.</p>
        
        <a href="/" class="button">Continue to App</a>
        <a href="/login" class="button button-secondary">Go to Login</a>
        
        <script>
            // Auto-redirect after 3 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
            
            // Handle URL parameters if needed
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            const type = urlParams.get('type');
            
            if (token && type === 'signup') {
                console.log('Email confirmation token received:', token);
                // You could store this token or send it to your app
            }
        </script>
    </div>
</body>
</html>
  `);
}
