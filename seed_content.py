"""
Forbidden Bourbon — Content Seed Script v2
Complete content library based on deep brand research.

IMPORTANT: Instagram limits hashtags to 5 per post (2026 change).
All content includes Instagram-optimized (5 max) hashtags.

Usage: python seed_content.py
"""

import sqlite3
import os
import database as db

DB_PATH = os.environ.get('DB_PATH', 'command_center.db')

def get_db():
    return db.get_db()

def seed():
    conn = get_db()
    cursor = conn.cursor()
    
    templates = [
        # PRODUCT EXCELLENCE
        ("Small Batch: The 50-Barrel Promise",
         "Most bourbon brands call anything under 200 barrels \"small batch.\" At Forbidden, our Small Batch Select never exceeds 50 barrels — and Master Distiller Marianne Eaves tastes every single one before blending. That's not marketing. That's a commitment.\n\nshop.drinkforbidden.com",
         "product", "#forbiddenbourbon #smallbatch #bourbon #craftbourbon #wheatedbourbon"),
        ("Why White Corn Matters",
         "Over 80% of yellow corn is grown for animal feed and industrial use. Forbidden uses food-grade white corn — the same quality you'd find in fine Southern cooking. Higher cost. Lower yield. Better bourbon.\n\nSome things are worth doing differently.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #whitecorn #craftspirits #wheatedbourbon"),
        ("The Lost Art of Low-Temp Fermentation",
         "In a 1910 Seagram's distillery manual, Marianne Eaves discovered a forgotten technique: low-temperature fermentation.\n\nStarting yeast at a lower temperature produces different, more complex flavors than the industry-standard high-heat method. A century-old secret, brought back to life in every bottle of Forbidden.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #distilling #craftspirits #innovation"),
        ("114 Proof. Zero Compromise.",
         "Our Single Barrel Bourbon is bottled at cask strength — 114 proof. Hand-selected by Marianne Eaves, each barrel tells its own story.\n\nBig creamy butterscotch on the palate, then a finish that goes down smooth before warming in your chest. We call it the magic trick.\n\ndrinkforbidden.com/products/single-barrel-bourbon",
         "product", "#forbiddenbourbon #singlebarrel #caskstrength #bourbon #whiskey"),
        ("Tasting Notes: Small Batch Select",
         "Nose: Vanilla bean, crème brûlée, hazelnut, a whisper of citrus\nPalate: Caramel, citrus oil, delicate floral, baking spices, oak sugar\nFinish: Creamy sweetness that lingers with oak and spice\n\n95.2 proof. Beautifully balanced. This is Forbidden.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #tastingnotes #bourbon #wheatedbourbon #bourbontasting"),
        ("The Mash Bill That Changed Everything",
         "75% white corn. 12% white winter wheat. 13% malted barley.\n\nForbidden has the highest malted barley percentage among major Kentucky bourbon producers. Every grain is food-grade, not feed-grade. The result: a bourbon that's sweet, complex, and unlike anything else on the shelf.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #wheatedbourbon #kentuckybourbon #craftbourbon"),
        ("Batch 3: Sweet Floral, Spice & Oak",
         "Small Batch Select, Batch 3. 50 barrels or fewer. 95.2 proof. Hand-blended by Marianne Eaves.\n\nNose: Sweet floral, spice and oak, dried tobacco leaf, citrus\nTaste: Warm spice, sorghum, oak sugar, dried fruit and baked bread\nFinish: Creamy, butter, sweet lingering warmth\n\nshop.drinkforbidden.com",
         "product", "#forbiddenbourbon #smallbatch #bourbon #tastingnotes #wheatedbourbon"),
        ("95.2 Proof. No Burn.",
         "How does a bourbon at 95.2 proof go down with virtually no burn? The secret is in the grain, the fermentation, and a master distiller who won't settle for anything less than perfection.\n\nTry it and see for yourself.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #whiskey #smoothbourbon #wheatedbourbon"),
        ("The Finish is the Star",
         "With Forbidden, the finish tells the story. Creamy vanilla, caramel, butter toffee, and charred oak dance together with almost no burn. Warm in the chest, smooth on the palate.\n\nThat's the Forbidden difference.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #tastingnotes #wheatedbourbon #craftbourbon"),
        ("Southern Roots, Southern Cooking",
         "Forbidden was inspired by Southern culinary tradition. Food-grade white corn. White winter wheat. Ingredients chosen the way a chef chooses — for flavor, not cost.\n\nBourbon with a chef's palate.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #southerncooking #foodgrade #craftbourbon"),
        ("Each Barrel Has a Story",
         "Each bottle of Single Barrel Forbidden Bourbon has its own unique character. Marianne Eaves hand-selects individual barrels that express the full range of Forbidden's one-of-a-kind flavor.\n\nNo two barrels are alike. No two bottles are the same.\n\ndrinkforbidden.com/products/single-barrel-bourbon",
         "product", "#forbiddenbourbon #singlebarrel #bourbon #craftbourbon #whiskey"),
        ("Art Deco Meets Bourbon",
         "The striking bottle. The metal label. The rigid lines. Forbidden isn't just what's inside — it's a statement on your shelf. Art-deco inspired design that matches the bold liquid within.\n\ndrinkforbidden.com",
         "product", "#forbiddenbourbon #bourbon #bottledesign #whiskey #luxury"),

        # MARIANNE EAVES / BRAND STORY
        ("Kentucky's First. Not Kentucky's Last.",
         "Marianne Eaves didn't just break the glass ceiling in bourbon — she shattered it. Kentucky's first female Master Distiller since Prohibition. Forbes 30 Under 30. Wine Enthusiast Top 40 Under 40.\n\nAnd now, the creator of Forbidden.\n\ndrinkforbidden.com/about",
         "brand", "#forbiddenbourbon #marianneeaves #womeninwhiskey #masterdistiller #bourbon"),
        ("From Brown-Forman to Forbidden",
         "Marianne Eaves started her career at Brown-Forman, where she became the first Master Taster at Woodford Reserve. She went on to make history at Castle & Key. She blended Sweetens Cove with Peyton Manning.\n\nAnd now — Forbidden. Nearly two decades of experience in every bottle.\n\ndrinkforbidden.com/about",
         "brand", "#forbiddenbourbon #marianneeaves #bourbon #masterdistiller #kentucky"),
        ("The Name Behind the Bourbon",
         "Until 1974, it was illegal for women to work in bourbon production in Kentucky. Marianne Eaves pushed against what everyone told her was impossible her entire career.\n\nThe name Forbidden isn't just a brand — it's her story.\n\nWhen nothing is forbidden, the outcome is perfection.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #marianneeaves #womeninspirits #bourbon #history"),
        ("200 Flavors in a Single Sip",
         "Master Distiller Marianne Eaves can distinguish over 200 individual flavors when tasting a bourbon. That sensory expertise — honed over nearly two decades — guides every blending decision in Forbidden.\n\nScience, art, and an extraordinary palate.\n\ndrinkforbidden.com/about",
         "brand", "#forbiddenbourbon #marianneeaves #masterdistiller #bourbon #bourbontasting"),
        ("Where Science Meets Art",
         "Marianne Eaves has a degree in Chemical Engineering. She started her career in art. Forbidden is what happens when analytical precision meets creative vision.\n\nA bourbon that's engineered for perfection and crafted with soul.\n\ndrinkforbidden.com/about",
         "brand", "#forbiddenbourbon #marianneeaves #bourbon #craftspirits #innovation"),
        ("As Seen on The TODAY Show",
         "When TODAY Show host Craig Melvin visited Bardstown, Kentucky and tasted Forbidden straight from the barrel, his reaction said it all. We appreciate the kind words, Craig.\n\nTry it yourself and see if you agree.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #todayshow #bourbon #bardstown #wheatedbourbon"),
        ("The Eaves Foundation",
         "Marianne Eaves isn't just making great bourbon — she's building a more inclusive industry. The Eaves Foundation supports innovation, education, and development of underrepresented communities in the spirits world.\n\nGreat bourbon. Greater purpose.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #marianneeaves #eavesfoundation #womeninwhiskey #bourbon"),
        ("Rebellion in Every Bottle",
         "Total creativity involves a certain degree of rebellion. To be completely creative, you tend to do things that are a little bit forbidden.\n\nThat's not just our philosophy — it's how we make bourbon.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #rebellion #bourbon #creativity #craftspirits"),
        ("Women in Whiskey",
         "Marianne Eaves made history. But she's not done. The bourbon world is evolving — more inclusive, more innovative, more exciting than ever.\n\nForbidden is proud to be part of that movement. Here's to every barrier broken and every expectation exceeded.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #womeninwhiskey #marianneeaves #bourbon #womeninspirits"),
        ("Bardstown Born",
         "Distilled, aged, and bottled at Bardstown Bourbon Company in the heart of Bourbon Country. Bardstown, Kentucky — where tradition lives and innovation thrives.\n\nThat's where Forbidden calls home.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #bardstown #kentucky #bourboncountry #bourbon"),
        ("A TEDx Stage & A Bourbon Barrel",
         "Marianne Eaves took the TEDx stage to talk about what bourbon and Broadway have in common: passion, vision, patience, science, art — and a fair amount of risk.\n\nThat same fearless approach is in every bottle of Forbidden.\n\ndrinkforbidden.com/about",
         "brand", "#forbiddenbourbon #marianneeaves #tedx #bourbon #innovation"),
        ("Grain to Glass",
         "Marianne Eaves controls every step — distillation, aging, blending, bottling. From selecting food-grade grains to hand-blending the final batch, nothing leaves without her approval.\n\nForbidden is grain to glass, in every sense.\n\ndrinkforbidden.com",
         "brand", "#forbiddenbourbon #graintoglass #bourbon #craftspirits #masterdistiller"),

        # COCKTAIL & PAIRING
        ("The Forbidden Old Fashioned",
         "The Forbidden Old Fashioned:\n\n2 oz Forbidden Small Batch\n1 sugar cube\n2-3 dashes Angostura bitters\nOrange peel\n\nMuddle sugar with bitters. Add bourbon and a large ice cube. Stir gently. Express the orange peel over the glass. The wheated profile makes this impossibly smooth.\n\ndrinkforbidden.com",
         "recipe", "#forbiddenbourbon #oldfashioned #cocktail #bourboncocktail #mixology"),
        ("Forbidden + Dark Chocolate",
         "The rich, wheated profile of Forbidden pairs beautifully with 70% dark chocolate. The bourbon's vanilla and caramel notes meet the chocolate's bitterness in a way that makes both better.\n\nPour. Bite. Repeat.\n\ndrinkforbidden.com",
         "pairing", "#forbiddenbourbon #chocolate #bourbonpairing #bourbon #foodpairing"),
        ("The Forbidden Whiskey Sour",
         "Forbidden Whiskey Sour:\n\n2 oz Forbidden Small Batch\n1 oz fresh lemon juice\n3/4 oz simple syrup\n1 egg white (optional)\n\nDry shake, then shake with ice. Strain into a coupe. The citrus notes in Forbidden make this cocktail sing.\n\ndrinkforbidden.com",
         "recipe", "#forbiddenbourbon #whiskeysour #cocktail #bourboncocktail #mixology"),
        ("Bourbon & Cheese Night",
         "Forbidden Small Batch + aged gouda = an evening well spent. The bourbon's caramel sweetness and the cheese's nutty richness play off each other perfectly.\n\nAdd some honeycomb and you've got a board worth talking about.\n\ndrinkforbidden.com",
         "pairing", "#forbiddenbourbon #bourbonandcheese #charcuterie #bourbon #datenight"),
        ("The Forbidden Manhattan",
         "The Forbidden Manhattan:\n\n2 oz Forbidden Small Batch\n1 oz sweet vermouth\n2 dashes Angostura bitters\nLuxardo cherry\n\nStir with ice for 30 seconds. Strain into a chilled coupe. The wheated bourbon's smooth, sweet profile was practically made for this classic.\n\ndrinkforbidden.com",
         "recipe", "#forbiddenbourbon #manhattan #cocktail #classiccocktail #mixology"),
        ("Summer Bourbon Lemonade",
         "Forbidden Summer Lemonade:\n\n2 oz Forbidden Small Batch\n3 oz fresh lemonade\nSplash of club soda\nMint sprig\n\nBuild over ice. Stir gently. The bourbon's citrus oil notes make this the most refreshing thing you'll pour all summer.\n\ndrinkforbidden.com",
         "recipe", "#forbiddenbourbon #bourbonlemonade #summercocktails #cocktail #bourbon"),
        ("Bourbon & Pecan Pie",
         "If you've never poured Forbidden alongside a slice of pecan pie, you're missing out on one of life's great pairings. The bourbon's butterscotch and vanilla meet the pie's caramelized sweetness.\n\nSouthern tradition at its finest.\n\ndrinkforbidden.com",
         "pairing", "#forbiddenbourbon #pecanpie #bourbonpairing #southern #bourbon"),
        ("The Forbidden Gold Rush",
         "Forbidden Gold Rush:\n\n2 oz Forbidden Small Batch\n3/4 oz honey syrup (equal parts honey + hot water)\n3/4 oz fresh lemon juice\n\nShake hard with ice. Strain over fresh ice. The honey brings out Forbidden's caramel notes like nothing else.\n\ndrinkforbidden.com",
         "recipe", "#forbiddenbourbon #goldrush #cocktail #honeycocktail #bourbon"),

        # BOURBON EDUCATION
        ("What is Wheated Bourbon?",
         "Most bourbons use rye as their secondary grain — it adds spice and bite. Wheated bourbons like Forbidden swap rye for wheat, creating a softer, sweeter, more approachable pour.\n\nOur white winter wheat takes it even further. The result: smooth, complex, and undeniably different.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #wheatedbourbon #bourbon #whiskey101 #bourboneducation"),
        ("What Does 'Small Batch' Actually Mean?",
         "Here's a secret: there's no legal definition for \"small batch\" bourbon. Some brands blend 200+ barrels and call it small batch.\n\nAt Forbidden, we cap it at 50 barrels — and Marianne Eaves tastes every single one. When we say small batch, we mean it.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #smallbatch #bourbon #bourbonfacts #craftbourbon"),
        ("Why Proof Matters",
         "Forbidden Small Batch is bottled at exactly 95.2 proof — not a random number. Marianne Eaves proofed it precisely to deliver maximum flavor while remaining smooth and approachable.\n\nToo low and you lose complexity. Too high and the heat takes over. 95.2 is the sweet spot.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #bourbon #bourbonproof #whiskey101 #craftspirits"),
        ("Single Barrel vs. Small Batch",
         "Small Batch: Multiple barrels blended for a consistent, balanced profile. Ours never exceeds 50.\n\nSingle Barrel: One barrel, one expression. Each bottle is unique, unrepeatable.\n\nBoth are Forbidden. Both are crafted by Marianne Eaves. The choice is yours.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #singlebarrel #smallbatch #bourbon #bourboneducation"),
        ("Food-Grade vs. Feed-Grade Grain",
         "Most bourbon is made with feed-grade corn — grown for livestock, not people. Forbidden uses food-grade white corn and white winter wheat. Same grains you'd find in fine Southern cooking.\n\nHigher cost, but you can taste the difference.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #bourbon #foodgrade #craftbourbon #whitecorn"),
        ("The Fermentation Secret",
         "Most distilleries ferment at high temperatures for speed. Forbidden uses low-temperature fermentation — a technique lost since 1910.\n\nLower temps mean yeast produces different, more complex flavor compounds. It takes longer. It's harder. It's worth it.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #fermentation #bourbon #distilling #craftspirits"),
        ("Wheat vs. Rye: Two Paths to Bourbon",
         "Rye bourbon brings spice, heat, and sharp edges. Wheated bourbon — like Forbidden — offers softness, sweetness, and depth.\n\nNeither is better. They're just different philosophies. Ours happens to use food-grade white winter wheat and a mash bill unlike anything else in Kentucky.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #wheatedbourbon #bourbon #ryebourbon #bourboneducation"),
        ("What Makes Bourbon, Bourbon?",
         "Made in the USA. At least 51% corn. Aged in new charred oak barrels. Distilled to no more than 160 proof. Entered the barrel at no more than 125 proof.\n\nForbidden meets every requirement — then goes further with food-grade grains, low-temp fermentation, and true small-batch blending.\n\ndrinkforbidden.com",
         "education", "#forbiddenbourbon #bourbon #whiskey101 #bourbonfacts #bourboneducation"),

        # ENGAGEMENT / COMMUNITY
        ("What's In Your Glass Tonight?",
         "Friday night. You've earned it. What's in your glass?\n\nWe know what's in ours.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #fridaynight #bourbon #bourbonlife #weekendvibes"),
        ("Neat, Rocks, or Cocktail?",
         "How do you take your Forbidden?\n\nNeat\nOn the rocks\nIn a cocktail\n\nThere's no wrong answer — but we want to hear yours.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #bourbon #neat #cocktails #bourboncommunity"),
        ("Tag Your Bourbon Buddy",
         "Everyone has that one friend who needs to try Forbidden. Tag them below.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #bourbon #bourboncommunity #whiskey #drinkforbidden"),
        ("Name a Better Duo",
         "Forbidden Small Batch + a fireplace. Name a better duo. We'll wait.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #bourbon #fireplace #bourbonlife #wintervibes"),
        ("Your First Forbidden",
         "Do you remember your first sip of Forbidden? That moment when you realized bourbon could be this smooth, this complex, this different?\n\nTell us about it.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #bourbon #firstsip #wheatedbourbon #bourboncommunity"),
        ("Weekend Plans: Sorted",
         "Step 1: Open Forbidden.\nStep 2: Pour generously.\nStep 3: There is no Step 3.\n\nHappy weekend from Forbidden Bourbon.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #weekend #bourbon #bourbonlife #weekendvibes"),
        ("Pour Something Forbidden",
         "Monday morning meetings. Tuesday deadlines. Wednesday grind. Thursday hustle. Friday?\n\nPour something Forbidden. You've earned it.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #friday #bourbon #bourbonlife #tgif"),
        ("Forbidden After Dark",
         "Good bourbon doesn't need an occasion. But a quiet evening, a comfortable chair, and a pour of Forbidden make any random Tuesday feel like something worth remembering.\n\ndrinkforbidden.com",
         "engagement", "#forbiddenbourbon #bourbon #eveningpour #bourbonlife #quietmoments"),

        # PRESS & SOCIAL PROOF
        ("Forbes Approved",
         "Forbes called Forbidden a terrific bourbon. We appreciate the recognition — but the best review is always the one you write yourself after your first sip.\n\nshop.drinkforbidden.com",
         "press", "#forbiddenbourbon #forbes #bourbonreview #bourbon #wheatedbourbon"),
        ("5 out of 5 Barrels",
         "The Bourbon Flight gave Forbidden a perfect 5/5 score and said it's worth every penny. We don't take that lightly.\n\ndrinkforbidden.com",
         "press", "#forbiddenbourbon #bourbonreview #bourbon #wheatedbourbon #craftbourbon"),
        ("Maxim Spirit of the Week",
         "When Maxim names you Spirit of the Week, sometimes that's all you need to hear.\n\nExperience Forbidden yourself: shop.drinkforbidden.com",
         "press", "#forbiddenbourbon #maxim #bourbon #whiskey #drinkforbidden"),
        ("Award-Winning Bourbon",
         "San Francisco. New York. Los Angeles. Denver. Ascot. Forbidden Bourbon has been recognized at spirits competitions around the world.\n\nBut the award that matters most? When you take that first sip and it changes what you thought bourbon could be.\n\ndrinkforbidden.com",
         "press", "#forbiddenbourbon #awards #bourbon #spiritscompetition #wheatedbourbon"),
        ("Garden & Gun Approved",
         "Featured in Garden & Gun's Holiday Gift Guide. If you're looking for a gift that says you have exceptional taste, Forbidden is it.\n\nshop.drinkforbidden.com",
         "press", "#forbiddenbourbon #gardenandgun #bourbon #giftguide #whiskey"),
        ("Drinkhacker: A- Rating",
         "Drinkhacker called Forbidden an exceedingly enjoyable and perfectly proofed whiskey, highlighting Marianne Eaves' deft blending touch.\n\nWe're proud of that one.\n\ndrinkforbidden.com",
         "press", "#forbiddenbourbon #bourbonreview #bourbon #drinkhacker #wheatedbourbon"),

        # SEASONAL / SALES
        ("Spring Sipping",
         "Warmer days call for lighter pours. Forbidden's citrus and floral notes shine when the weather turns. Try it over a single large ice cube on the porch — let it open up slowly as the evening does.\n\ndrinkforbidden.com",
         "seasonal", "#forbiddenbourbon #spring #bourbon #porchpour #bourbonlife"),
        ("Date Night, Elevated",
         "Planning date night? Forbidden Small Batch, two glasses, and good conversation. The bourbon does the rest.\n\nSometimes the simplest plans are the best ones.\n\ndrinkforbidden.com",
         "seasonal", "#forbiddenbourbon #datenight #bourbon #bourbonlife #couples"),
        ("Find Forbidden Near You",
         "Looking for Forbidden at a store near you? Our store locator makes it easy. Enter your zip code and find your next bottle.\n\ndrinkforbidden.com/store-locator",
         "sales", "#forbiddenbourbon #bourbon #storelocator #wheatedbourbon #shopnow"),
        ("The Perfect Gift",
         "Not sure what to give? Forbidden Bourbon. The distinctive art-deco bottle. The incredible liquid inside. The story of Kentucky's first female Master Distiller.\n\nIt's more than a gift — it's a conversation starter.\n\nshop.drinkforbidden.com",
         "sales", "#forbiddenbourbon #bourbon #giftidea #whiskey #bourbongift"),
        ("Collectible & Drinkable",
         "The striking art-deco bottle, the metal label, the limited batches. Forbidden is absolutely collectible. But the best part? It's even better when you open it.\n\nshop.drinkforbidden.com",
         "sales", "#forbiddenbourbon #bourbon #collectible #whiskey #bourboncollection"),
        ("Available at Total Wine",
         "Looking for Forbidden? You can find our Small Batch Select at Total Wine locations and online. 4.5 stars from their customers — and counting.\n\ndrinkforbidden.com/store-locator",
         "sales", "#forbiddenbourbon #totalwine #bourbon #wheatedbourbon #shopnow"),

        # EVENTS & INDUSTRY
        ("Bourbon Festival Season",
         "Bourbon festival season is heating up. If you see Forbidden at a tasting event, stop by and say hello. Better yet — try the Single Barrel side by side with the Small Batch. You'll see why we make both.\n\ndrinkforbidden.com",
         "events", "#forbiddenbourbon #bourbonfestival #bourbon #whiskeyfestival #bourbontasting"),
        ("Meet the Maker",
         "There's nothing like hearing the story behind the bourbon from the person who made it. Marianne Eaves regularly hosts tastings and meet-and-greets across the country.\n\nFollow us for upcoming event announcements.\n\ndrinkforbidden.com",
         "events", "#forbiddenbourbon #marianneeaves #meetthemaker #bourbon #bourbonevent"),
        ("Bourbon & Beyond 2026",
         "Bourbon & Beyond returns to Louisville September 24-27, 2026. The world's largest bourbon, food, and music festival — right in the heart of bourbon country.\n\nWill we see you there?\n\nbourbonandbeyond.com",
         "events", "#forbiddenbourbon #bourbonandbeyond #louisville #bourbonfestival #kentucky"),
        ("The Future of Bourbon",
         "The bourbon industry is evolving. More women distillers. More innovation in grains and fermentation. More thoughtful, craft-focused producers.\n\nForbidden has been part of this movement since day one. The future tastes incredible.\n\ndrinkforbidden.com",
         "industry", "#forbiddenbourbon #bourbon #bourbonculture #innovation #craftspirits"),
        ("Support Craft, Support Flavor",
         "In a world of mass-produced spirits, choosing craft bourbon matters. When you pour Forbidden, you're supporting a Master Distiller who tastes every barrel, uses food-grade grains, and refuses to cut corners.\n\nThat's worth supporting.\n\nshop.drinkforbidden.com",
         "industry", "#forbiddenbourbon #craftbourbon #bourbon #supportcraft #smallbatch"),
        ("Bourbon Country, Kentucky",
         "Bardstown, Kentucky. The Bourbon Capital of the World. Home to Bardstown Bourbon Company, where every drop of Forbidden is distilled, aged, and bottled.\n\nIf you haven't visited bourbon country yet, put it on your list.\n\ndrinkforbidden.com",
         "events", "#forbiddenbourbon #bardstown #kentucky #bourboncountry #bourbontrail"),
        # HOLIDAY COCKTAILS
        ("Holiday Whiskey Sour",
         "The Forbidden Holiday Whiskey Sour 🎄\n\n2 oz Forbidden Small Batch Select\n1 oz fresh lemon juice\n¾ oz simple syrup\n1 egg white\nGarnish: rosemary sprig, cranberries\n\nDry shake, wet shake, strain, and garnish with a rosemary sprig and fresh cranberries. The perfect holiday cocktail.\n\ndrinkforbidden.com",
         "cocktails", "#forbiddenbourbon #whiskeysour #holidaycocktails #bourbon #cocktailrecipe"),
        ("Holiday Entertaining with Forbidden",
         "Hosting this holiday season? Skip the generic wine and wow your guests with a Forbidden cocktail station.\n\nSet out a bottle of Small Batch Select, fresh citrus, rosemary, cranberries, and simple syrup. Let everyone make their own Holiday Whiskey Sour.\n\nEasy. Elegant. Unforgettable.\n\nshop.drinkforbidden.com",
         "cocktails", "#forbiddenbourbon #holidayentertaining #bourboncocktails #hostess #cheers"),
        ("Winter Warmth in a Glass",
         "There's something about a well-made bourbon cocktail by the fire that just hits different in winter. Forbidden Small Batch Select — wheated for extra warmth, smooth enough for sipping, bold enough for mixing.\n\nWhat's your cold-weather pour?\n\ndrinkforbidden.com",
         "seasonal", "#forbiddenbourbon #wintercocktails #bourbon #fireside #whiskeylover"),
        ("Forbidden Gift Guide",
         "Still looking for the perfect gift? 🎁\n\nForbidden Small Batch Select — for the bourbon curious\nForbidden Single Barrel — for the collector\n\nBoth ship direct. Both say \"I have excellent taste.\"\n\nshop.drinkforbidden.com",
         "seasonal", "#forbiddenbourbon #giftguide #bourbongifts #whiskeygift #holidaygifts"),
        ("New Year's Toast with Forbidden",
         "Ring in the new year with something bold.\n\nForget the champagne — raise a glass of Forbidden Small Batch Select at midnight. Wheated bourbon. Kentucky crafted. A new tradition worth starting.\n\nHappy New Year from the Forbidden family. 🥃\n\ndrinkforbidden.com",
         "seasonal", "#forbiddenbourbon #newyears #bourbontoast #cheers #newyearnewpour"),
        ("Cocktail Hour: Forbidden Old Fashioned",
         "The Forbidden Old Fashioned ✨\n\n2 oz Forbidden Single Barrel\n1 sugar cube\n2-3 dashes Angostura bitters\nOrange peel\n\nMuddle sugar and bitters. Add bourbon, stir with ice, express orange peel over the glass. The Single Barrel's caramel and vanilla notes make this one unforgettable.\n\ndrinkforbidden.com",
         "cocktails", "#forbiddenbourbon #oldfashioned #cocktail #bourbon #mixology"),
        ("Summer Bourbon Smash",
         "The Forbidden Bourbon Smash ☀️\n\n2 oz Forbidden Small Batch Select\n1 oz fresh lemon juice\n¾ oz simple syrup\n6-8 fresh mint leaves\n\nMuddle mint with syrup and lemon. Add bourbon, shake with ice, strain over crushed ice. Garnish with mint bouquet.\n\nSummer in a glass.\n\ndrinkforbidden.com",
         "cocktails", "#forbiddenbourbon #bourbonsmash #summercocktails #bourbon #mintcocktail"),
        ("DTC: Get Forbidden Delivered",
         "Forbidden Bourbon is now available for direct-to-consumer shipping through Mash Networks. Order from your couch, delivered to your door.\n\nNo hunting shelves. No settling for substitutes.\n\nshop.drinkforbidden.com",
         "product", "#forbiddenbourbon #bourbondelivery #dtc #shopbourbon #craftbourbon"),
    ]
    
    added = 0
    for title, content, category, hashtags in templates:
        existing = db._fetchone(conn, 'SELECT id FROM content_templates WHERE title = ?', (title,))
        if not existing:
            if db.USE_POSTGRES:
                conn.cursor().execute('INSERT INTO content_templates (title, content, category, hashtags) VALUES (%s, %s, %s, %s)',
                             (title, content, category, hashtags))
            else:
                cursor.execute('INSERT INTO content_templates (title, content, category, hashtags) VALUES (?, ?, ?, ?)',
                             (title, content, category, hashtags))
            added += 1
            print(f"  + {title}")
    
    # HASHTAG GROUPS (Instagram = max 5, other platforms = more)
    new_groups = [
        ('IG: Product', '#forbiddenbourbon #bourbon #wheatedbourbon #craftbourbon #smallbatch'),
        ('IG: Marianne', '#forbiddenbourbon #marianneeaves #womeninwhiskey #masterdistiller #bourbon'),
        ('IG: Cocktails', '#forbiddenbourbon #cocktail #mixology #bourboncocktail #drinkforbidden'),
        ('IG: Education', '#forbiddenbourbon #bourbon #whiskey101 #bourboneducation #craftspirits'),
        ('IG: Lifestyle', '#forbiddenbourbon #bourbonlife #bourbon #weekendvibes #whiskey'),
        ('IG: Press', '#forbiddenbourbon #bourbonreview #bourbon #wheatedbourbon #awards'),
        ('IG: Events', '#forbiddenbourbon #bourbonfestival #bourbon #kentucky #bourbontasting'),
        ('Twitter: Full', '#ForbiddenBourbon #bourbon #wheatedbourbon #MarianneEaves #KentuckyBourbon #WomenInWhiskey #craftbourbon #drinkforbidden'),
        ('Bluesky: Full', '#ForbiddenBourbon #bourbon #wheatedbourbon #MarianneEaves #craftbourbon #KentuckyBourbon'),
    ]
    
    groups_added = 0
    for name, hashtags in new_groups:
        existing = db._fetchone(conn, 'SELECT id FROM hashtag_groups WHERE name = ?', (name,))
        if not existing:
            if db.USE_POSTGRES:
                conn.cursor().execute('INSERT INTO hashtag_groups (name, hashtags) VALUES (%s, %s)', (name, hashtags))
            else:
                cursor.execute('INSERT INTO hashtag_groups (name, hashtags) VALUES (?, ?)', (name, hashtags))
            groups_added += 1
    
    conn.commit()
    conn.close()
    print(f"\n  Content seeded: {added} templates, {groups_added} hashtag groups")
    print(f"  NOTE: Instagram now limits to 5 hashtags per post (2026)")

if __name__ == '__main__':
    seed()
