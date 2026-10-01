import json, os, re
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

HOME_FALLBACK = {
 "title":"Home Interior Plan", "summary":"A balanced starter plan for the requested room and budget.",
 "budget_allocation":[{"category":"Lighting","percentage":15},{"category":"Furniture","percentage":45},{"category":"Decor","percentage":20},{"category":"Storage","percentage":20}],
 "suggestions":[
  {"item":"Warm LED lighting set","category":"Lighting","estimated_price":1800,"platform":"Amazon","reason":"Energy-efficient and suitable for layered room lighting."},
  {"item":"Compact multipurpose table","category":"Furniture","estimated_price":6500,"platform":"IKEA","reason":"Useful for flexible dining or workspace needs."},
  {"item":"Textured cushion set","category":"Decor","estimated_price":1200,"platform":"Amazon","reason":"Adds color and comfort without consuming much budget."},
  {"item":"Modular storage cabinet","category":"Storage","estimated_price":4500,"platform":"IKEA","reason":"Adds practical storage while keeping the room organized."}
 ]}
PARTY_FALLBACK = {
 "title":"Party Budget Plan", "summary":"A practical event allocation based on guests, event type and venue.",
 "budget_allocation":[{"category":"Catering","percentage":50},{"category":"Decoration","percentage":20},{"category":"Entertainment","percentage":15},{"category":"Venue/Other","percentage":15}],
 "suggestions":[
  {"item":"Per-guest catering package","category":"Catering","estimated_price":0,"platform":"Zomato / Swiggy","reason":"Scale the menu to guest count and protect the core food budget."},
  {"item":"Theme decoration package","category":"Decoration","estimated_price":0,"platform":"Local vendor","reason":"Choose a simple theme to control setup and material costs."},
  {"item":"Music / speaker setup","category":"Entertainment","estimated_price":0,"platform":"Local vendor","reason":"A compact setup keeps entertainment within a modest allocation."}
 ]}
JEWELRY_FALLBACK = {
 "title":"Jewelry Style Plan", "summary":"Occasion-aware jewelry ideas matched to the requested style and budget.",
 "suggestions":[
  {"item":"Minimal pendant necklace","category":"Neckwear","estimated_price":2500,"platform":"Amazon","reason":"Versatile for everyday and semi-formal outfits."},
  {"item":"Statement earrings","category":"Earrings","estimated_price":1800,"platform":"Flipkart","reason":"Adds a focal point for festive or evening styling."},
  {"item":"Slim bangle set","category":"Bangles","estimated_price":2200,"platform":"Amazon","reason":"Works well with traditional styling without dominating the outfit."},
  {"item":"Classic ring","category":"Ring","estimated_price":1500,"platform":"Flipkart","reason":"A simple finishing piece that complements multiple looks."}
 ]}

def parse_ai_json(text):
    if not text: return None
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try: return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try: return json.loads(m.group(0))
            except Exception: return None
    return None

def _prompt(kind, d):
    common = "Return ONLY valid JSON. Do not claim live prices or live availability. Use estimated INR prices and label platforms as suggested sources. Keep the total recommendation realistic for the budget. JSON keys: title, summary, budget_allocation (optional list), suggestions (list of objects with item, category, estimated_price, platform, reason)."
    if kind == "home": return f"You are PocketSmart AI Home Interior Planner. Budget INR {d.get('budget')}. Rooms: {d.get('rooms','')}. Quantities/details: {d.get('quantities','')}. Style: {d.get('style','')}. Recommend furniture, lighting and decor using sources such as IKEA and Amazon. {common}"
    if kind == "party": return f"You are PocketSmart AI Party Planner. Budget INR {d.get('budget')}. Guests: {d.get('guests')}. Event: {d.get('event_type','')}. Venue: {d.get('venue','')}. Food preference: {d.get('food_preference','')}. {common} Include catering, decoration and entertainment allocation. Mention Swiggy/Zomato/OYO only as suggested platforms where relevant."
    return f"You are PocketSmart AI Jewelry Planner. Budget INR {d.get('budget')}. Occasion: {d.get('occasion','')}. Style: {d.get('style','')}. Outfit notes: {d.get('outfit_notes','')}. Consider the optional outfit image for color/style coordination. Recommend jewelry from sources such as Amazon and Flipkart. {common}"

def generate_recommendation(kind, data, image_bytes: Optional[bytes]=None, image_mime: Optional[str]=None):
    fallback = {"home":HOME_FALLBACK,"party":PARTY_FALLBACK,"jewelry":JEWELRY_FALLBACK}.get(kind, HOME_FALLBACK)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return {**fallback, "mode":"demo", "note":"Demo fallback is active. Add GEMINI_API_KEY to enable Gemini-generated recommendations."}
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        contents = [_prompt(kind, data)]
        if image_bytes and image_mime:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
        response = client.models.generate_content(model=MODEL, contents=contents)
        parsed = parse_ai_json(response.text)
        if isinstance(parsed, dict) and isinstance(parsed.get("suggestions"), list) and parsed["suggestions"]:
            parsed["mode"] = "gemini"; return parsed
    except Exception as exc:
        return {**fallback, "mode":"fallback", "note":f"Gemini was unavailable, so a default plan was returned: {type(exc).__name__}."}
    return {**fallback, "mode":"fallback", "note":"Gemini returned an incomplete result, so a default plan was returned."}
