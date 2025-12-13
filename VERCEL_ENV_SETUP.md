# Setting Up Environment Variables on Vercel

Your AI summary feature is not working because Vercel doesn't automatically load the `.env` file. You need to manually configure the environment variables in the Vercel dashboard.

## Steps to Configure GEMINI_API_KEY on Vercel

1. **Go to your Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Select your project: `brand-echo-sentiment`

2. **Navigate to Settings**
   - Click on the "Settings" tab at the top

3. **Add Environment Variables**
   - In the left sidebar, click "Environment Variables"
   - Click "Add New" button

4. **Add GEMINI_API_KEY**
   - **Name**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyDkqEYTKKsKhYCxpv41FE5JfXRvrqlnMmE`
   - **Environment**: Select all environments (Production, Preview, Development)
   - Click "Save"

5. **Redeploy Your Application**
   - After adding the environment variable, go to the "Deployments" tab
   - Click the three dots (`...`) on your latest deployment
   - Click "Redeploy"
   - Wait for the deployment to complete

6. **Verify**
   - Once redeployed, test your application at https://brand-echo-sentiment.vercel.app/
   - Try analyzing a brand like "Apple"
   - The AI summary should now appear

## Optional: Add Other Environment Variables

If you want to use NewsAPI for real-time data (currently using sample data), also add:

- **Name**: `NEWSAPI_KEY`
- **Value**: (Get a free API key from https://newsapi.org/)

## Troubleshooting

If the AI summary still doesn't appear after deployment:

1. Check Vercel logs:
   - Go to your deployment
   - Click "View Function Logs"
   - Look for errors related to GEMINI_API_KEY

2. Common issues:
   - API key might be invalid or expired
   - Rate limits on Gemini API
   - Network issues from Vercel's servers

3. Check the response in browser console:
   - Open Developer Tools (F12)
   - Go to Network tab
   - Analyze the brand
   - Check the response from `/analyze-brand` endpoint
   - Look for the `ai_summary` field in the JSON response
