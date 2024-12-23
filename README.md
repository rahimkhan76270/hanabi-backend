# Hanabi Sentiment Analysis Backend

This is the backend of the two part app of sentiment analysis app. Frontend can be found at <https://github.com/rahimkhan76270/hanabi-frontend.git>. To run this app locally follow the following steps:-

### Step 1

clone the repo using the command

```bash
git clone https://github.com/rahimkhan76270/hanabi-backend.git
```

now go to the folder hanabi-backend using the command

```bash
cd hanabi-backend
```

### Step 2

First make the conda environment using the command

```bash
conda create --name env python=3.10
```

Now activate the environment using the command

```bash
conda activate env
```

Now install the dependencies using the command

```bash
pip install -r requirements.txt
```

I have left two dependencies ```torch``` and ```transformers``` because torch installs nvidia dependencies by default. Sometimes we don't want to run our models on GPU so these dependencies are redundant and use a lot of space on the disk. So to prevent this we can install the only CPU version of ```torch``` using the following command

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

if you want to install GPU version of torch run the following command

```bash
pip install torch
```

finally install ```transformers```

```bash
pip install transformers
```

### Step 3

Run the app using the following command

```bash
uvicorn app:app
```

it will run the server on the port 8000. Now open the browser and access the link <http://localhost:8000/> it will show the message ```Hello World```.
it has 4 endpoints

#### Home

this is the default page which accepts only get requests

```bash
http://localhost:8000/
```

and sends the reponse

```json
{
    "message" : "hello world"
}
```

#### Signup

This function is used for sign up. It accepts only post requests.

```bash
http://localhost:8000/signup/
```

request format is the following

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

Password should be atleast 8 characters long. Password should contain atleast one number and one letter. After successful signup it will return the followind reponse

```json
{
    "response":"successful"
}
```

#### login

This function accepts the post requests

```bash
http://localhost:8000/login/
```

the request format is

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

after success it will return a ```JWT``` token which will be used to authenticate further.

```json
{
  "token": "some token"
}
```

#### Upload csv

This endpoint accepts the post requests and user should have the authentication token in the header to access it. It accepts a multipart form data type csv file.

```bash
http://localhost:8000/upload-csv/
```

request format

```json
formData,
 {
    headers:{ 
                "Content-Type": "multipart/form-data", "Authorization": `Bearer {token`},
            }
 }
```

after completion it will return the counts of the sentiments and the data.

```json
{
    "user": email,
    "sentiment_counts": sentiment_counts,
    "sentiments": list(sentiment_records.values())
}
```

I have used ```tabularisai/multilingual-sentiment-analysis``` from ```huggingface``` for sentiment prediction. It classifies the text into the following categories  Very Negative, Negative, Neutral, Positive, Very Positive). It is multilingual based on ```distilbert/distilbert-base-multilingual-cased```
Supports English plus Chinese (中文), Spanish (Español), Hindi (हिन्दी), Arabic (العربية), Bengali (বাংলা), Portuguese (Português), Russian (Русский), Japanese (日本語), German (Deutsch), Malay (Bahasa Melayu), Telugu (తెలుగు), Vietnamese (Tiếng Việt), Korean (한국어), French (Français), Turkish (Türkçe), Italian (Italiano), Polish (Polski), Ukrainian (Українська), Tagalog, Dutch (Nederlands), Swiss German (Schweizerdeutsch).
I have deployed it on ```Huggingface Spaces``` using docker can be accessed here. <https://rahim-khan-iitg-sentiment-analysis.hf.space/>
