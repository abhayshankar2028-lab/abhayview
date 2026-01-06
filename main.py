import os, feedparser, datetime, random, re
from huggingface_hub import InferenceClient

FEEDS = {
    "Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/"
}

def extract_content(text, tag, next_tag=None):
    try:
        start = text.find(tag) + len(tag)
        end = text.find(next_tag) if next_tag else None
        return text[start:end].strip()
    except: return ""

def run():
    cat, url = random.choice(list(FEEDS.items()))
    feed = feedparser.parse(url)
    article = feed.entries[0]
    
    client = InferenceClient(token=os.environ.get("HF_TOKEN"))
    prompt = f"ACT AS: Harsha Bhogle. Write a 150-word poetic story about: {article.title}. FORMAT: TITLE: [Title] SEO_DESC: [Desc] TAGS: [Tag1, Tag2] BODY: [Story]"
    
    res = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": prompt}], max_tokens=800)
    text = res.choices[0].message.content

    title = extract_content(text, "TITLE:", "SEO_DESC:").replace('"', '')
    desc = extract_content(text, "SEO_DESC:", "TAGS:").replace('"', '')
    body = extract_content(text, "BODY:")
    img = article.media_content[0]['url'] if hasattr(article, 'media_content') else ""

    fn = f"_posts/{datetime.date.today()}-{re.sub(r'[^a-z0-9]', '-', title.lower()[:30])}.md"
    with open(fn, "w") as f:
        f.write(f'---\nlayout: post\ntitle: "{title}"\ndescription: |\n  {desc}\nimage: "{img}"\n---\n\n{body}')

if __name__ == "__main__":
    run()
