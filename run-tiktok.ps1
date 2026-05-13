$inputJson = '{"search":"github skills","limit":5}'
$actor = "clockworks/tiktok-scraper"
$format = "json"
$script = "E:\workspace\skills\apify-ultimate-scraper\reference\scripts\run_actor.js"

& node $script --actor=$actor --input=$inputJson --format=$format
