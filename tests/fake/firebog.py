# https://v.firebog.net/hosts/lists.php?type=tick
firebog_tick_lists = """https://v.firebog.net/hosts/AdguardDNS.txt
https://v.firebog.net/hosts/static/w3kbl.txt"""

firebog_adguard_list = """# AdguardDNS, parsed and mirrored by https://firebog.net
# Updated 02OCT24 from https://filters.adtidy.org/extension/chromium/filters/15.txt

# This is sourced from an "adblock" style list which is flat-out NOT designed to work with DNS sinkholes
# There WILL be mistakes with how this is parsed, due to how domain names are extracted and exceptions handled
# Please bring any parsing issues up at https://github.com/WaLLy3K/wally3k.github.io/issues prior to raising a request upstream

# If your issue IS STILL PRESENT when using uBlock/ABP/etc, you should request a correction at https://github.com/AdguardTeam/AdGuardSDNSFilter/issues

0024ad98dd.com
002777.xyz
003store.com
00701059.xyz
"""

firebog_w3kbl_list = """# Personal Blocklist by WaLLy3K (https://firebog.net/about)
# Content added to this list has been manually verified, and is updated irregularly

# Licensing: CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)
## You are welcome to copy, redistibute, remix, transform and build upon this content
## You must give appropriate credit and indicate if changes were made

## Addtionally, you may even use this commercially
## However in the spirit of open-source, I strongly urge a small reoccuring donation to help cover server costs:
## https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=HU4EDJZP2S9QA

## Ads ##
yt.moatads.com
us.intellitxt.com
evolveplatform.net
"""

firebog_malware = """# RPiList-Malware, parsed and mirrored by https://firebog.net
# Updated 30SEP24 from https://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/malware

# If your issue IS STILL PRESENT when using uBlock/ABP/etc, you should request a correction at https://github.com/RPiList/specials/issues

||0-0-0-birkart-clws-ifs-globalmn.net.daraz.com^
||0-0-stagemn.net.daraz.com^
||0-009.0-132.net.daraz.com^
||0-00d10140000motieas-990auyn11w0wpnuy4.dcsportal.0-astrologie.net.daraz.com^
||0-00d10140100motieas-990auyn11w0wpnuy4.net.daraz.com^
||0-00d30000000z4uceak.0-astrologie.net.daraz.com^
||0-00d30000000z4uceak.net.daraz.com^
"""
