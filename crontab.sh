# Update database once a month on the 15th
00 5 15 * * flask update-centers
15 5 15 * * flask geocode
30 5 15 * * flask purge-centers
