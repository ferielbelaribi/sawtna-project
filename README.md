Sawtna – AI-Powered Safe Palestine Content Posting App
        🌟 Introduction:
            Social media platforms like Facebook, Instagram, Twitter/X, and Telegram use automated moderation systems. These often:
           ❌ Delete images or videos related to Palestine.
           ⚠️ Restrict or ban accounts (shadowban).
           😔 Silence journalists and activists.
           Sawtna (صوتنا – "Our Voice") is an AI-powered mobile app designed to help Palestinians and activists:   
           🛡️ Share their stories without being censored.
           🤖 Automatically check whether content (image or text) will likely be flagged.
           ✨ Modify risky content (blur, rewrite) while preserving the message.
        
        📊 Dataset Collection:
           📌 Sources:
           Facebook → Public pages and groups.
           Instagram → Hashtags like #Gaza, #FreePalestine.
           Twitter/X → Trending hashtags, activist accounts.
           Telegram → Public resistance/solidarity channels.

           📸 Image Dataset
           Each image was manually labeled into two categories:
           ✅ Allowed → Safe for posting (e.g., Palestinian flag, peaceful protest).
           ⚠️ At Risk → Likely to be removed (e.g., visible blood, corpses, destruction).
           📝 Text Dataset
           Collected captions from the same sources in Arabic & English and also labeled into two categories(Allowed,At Risk)
        
        🚀 Core Features:
            1️⃣ Image Classification
             Deep learning model (VIT).
             Input: an image → Output: Allowed / At Risk.
             2️⃣ Image Filtering (Risk Reduction):If the image is "At Risk":
             Use segmentation models (SAM) to detect sensitive regions (blood, corpses).
             Apply one of the following filters like Gaussian Blur → smooth blur.
              ✅ Final result = an image that conveys the message but avoids deletion.
            3️⃣ Text Classification:
             Transformer model (XLM-RoBERTa).
             Input: caption text → Output: Allowed / At Risk
             4️⃣ Text Re-Generation:
             If text is “At Risk”:Automatically rewrite it into safer language while keeping meaning.
             5️⃣ Text-to-Image Generation (API):
             Integrated with Pollinations API / Stable Diffusion.
             create artistic images from prompts.
        
        🛠️ Tech Stack:
             Frontend (Mobile App): Flutter
             Backend & AI Models: Python, PyTorch,FAST API
             Computer Vision: VIT, SAM
             NLP: MARBERT (Arabic BERT), mBERT
             Image Generation: Stable Diffusion v1.5, Pollinations API
             Data Storage: Google Drive, CSV files

        📊 Workflow: The application works in a pipeline where each user input passes through several AI models before producing the final safe content
             1️⃣ User Upload:The user uploads:
              Image (from their gallery or camera)
              Caption (text description they want to post)
             2️⃣ AI Moderation Check :The system applies two classifiers:
              Image Classifier → Analyzes the photo to decide:
              ✅ Allowed → Safe to publish.
              ⚠️ At Risk → Might be censored by platforms (contains blood, corpses, destroyed houses, etc.).
              Text Classifier → Analyzes the caption text:
              ✅ Allowed → Neutral/safe text.
              ⚠️ At Risk → Contains sensitive words that trigger censorship (e.g., “martyr”, “terrorist”, “kill”)
              3️⃣ Risk Handling:If either the image or caption is At Risk:
              -Image Processing (Computer Vision):
               The app segments the risky regions (blood, corpses, wounds).
               A filter is applied to hide shocking details:Blur, Pixelation, Fog/mask
              -Text Processing (NLP):If the caption is risky, the app rewrites it automatically.
              This ensures the meaning is preserved but the post is less likely to be flagged.
              -Safe Image Generation (API):
               If the user prefers to avoid uploading real photos, they can use AI Image Generation.


        🎨 Branding Guidelines:
             Colors: Palestinian flag palette
             Red: #D32F2F
             Green: #1B5E20
             Black: #000000
             White: #FFFFFF
             Fonts:
             Arabic: Tajawal
             English: Montserrat
             Style:
             Clean, minimal UI.
             Realistic or artistic visual assets

        📈 Evaluation:
            -Image Classifier: Measured using Accuracy, Precision, Recall, F1-score.
            -Text Classifier: Evaluated with confusion matrix + precision/recall.
            -Filtering Model: User evaluation (how well shocking parts are hidden).
            -Text Regeneration: BLEU / semantic similarity scores.

        🧭 Future Work:
            -📹 Extend to videos → blur sensitive frames.
            -🌍 Multi-language support (Arabic, English, French).
            -🔒 Add Differential Privacy to protect user data.
            -☁️ Deploy models as REST API (FastAPI) for easy integration.
        
        ✊ Mission
            Sawtna is more than an app.
            It is a tool to protect Palestinian voices online, ensuring stories can be shared freely while bypassing unfair censorship
        



