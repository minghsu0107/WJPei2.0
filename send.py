from qmonitor import store
from slack import WebClient

SUMMARY = '''
*Total mails in queue*: `{total_mails}`
*Total queue size*: `{total_mails_size:.3}` MB

*Mails by accepted date*
last 24h: `{mails_by_age[last_24h]}`
1 to 4 days ago: `{mails_by_age[1_to_4_days_ago]}`
older than 4 days: `{mails_by_age[older_than_4_days]}`

*Mails by status*
Active: `{active_mails}`
Hold: `{hold_mails}`
Deferred: `{deferred_mails}`

*Mails by size*
Average size: `{average_mail_size:.3f}` KB
Maximum size: `{max_mail_size:.3f}` KB
Minimum size: `{min_mail_size:.3f}` KB

*Unique senders*
Senders: `{unique_senders}`
Domains: `{u_s_domains}`

*Unique recipients*
Recipients: `{unique_recipients}`
Domains: `{u_r_domains}`

*Top senders*
{top_senders}

*Top sender domains*
{top_sender_domains}

*Top recipients*
{top_recipients}

*Top recipient domains*
{top_recipient_domains}
'''

def generateResult():
    pstore = store.PostqueueStore()
    pstore.load()
    data = pstore.summary()
    data['total_mails_size'] /= 1024*1024.0
    data['average_mail_size'] /= 1024.0
    data['max_mail_size'] /= 1024.0
    data['min_mail_size'] /= 1024.0
    data['u_s_domains'] = data['unique_sender_domains']
    data['u_r_domains'] = data['unique_recipient_domains']
    for status in data['top_status']:
        data[status[0] + '_mails'] = status[1]

    ranks = ['top_senders', 'top_sender_domains',
             'top_recipients', 'top_recipient_domains']
    for key in ranks:
        data[key] = "\n".join(["%-4s  %s" % (value[1], value[0])
                               for value in data[key]])

    return SUMMARY.format(**data)

def send_report(token_file, channel):
    with open(token_file, 'r') as f:
        token = f.read().strip()

        client = WebClient(token=token)
        client.chat_postMessage(
            channel=channel,
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': generateResult()
                    }
                }
            ]
        )

if __name__ == "__main__":
    send_report('nasalab-token', 'slackbot-test')