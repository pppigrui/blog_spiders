h = """
<error>
        <ret>0</ret>
        <message></message>
        <skey>@crypt_6ca2f576_b502613040001fcbc0ccf59165bd8782</skey>
        <wxsid>IQso/ovzSZK9SpEC</wxsid>
        <wxuin>518407033</wxuin>
        <pass_ticket>33sMB9RozwRSPGI3k3pOM0JV/24FpdeDQs7gL+t3QUe8EaGXpgYqaQJYxPx8GDhB</pass_ticket>
        <isgrayscale>1</isgrayscale>
        </error>
"""
from lxml import etree
html = etree.HTML(h)
ticket_dict = {}
skey = html.xpath('//skey/text()')[0]
ret = html.xpath('//ret/text()')[0]
wxsid = html.xpath('//wxsid/text()')[0]
wxuin = html.xpath('//wxuin/text()')[0]
pass_ticket = html.xpath('//pass_ticket/text()')[0]
isgrayscale = html.xpath('//isgrayscale/text()')[0]
ticket_dict['skey'] = skey
ticket_dict['ret'] = ret
ticket_dict['wxsid'] = wxsid
ticket_dict['wxuin'] = wxuin
ticket_dict['pass_ticket'] = pass_ticket
ticket_dict['isgrayscale'] = isgrayscale
print(ticket_dict)


