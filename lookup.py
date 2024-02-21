import dns.resolver



def get_spf_record(domains):

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8',  '1.1.1.1', ]
    with open('txt_records.txt', 'w') as w:
        for domain in domains:
            try:
                spf_record = resolver.resolve(domain, 'TXT')
                # print(f"\nSPF & TXT Records for {domain}:")
                # print("|", end='') 
                print(domain)
                for record_data in spf_record:
                    
                    for string_data in record_data.strings:
                        # print TXT string data which starts with SPF version
                        if string_data.decode().startswith('v=spf1'):
                            for record in string_data.decode().split(' '):
                                if record.startswith('include'):
                                    w.write(f"SPF;{record};{domain}\n")
                        else:

                            w.write(f"TXT;{string_data.decode()};{domain}\n")

            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass
                # print(f"No SPF record found for {domain}")
            except Exception as e:
                print(f"Exception {str(e)},{domain}")
                # print(f"Error occurred while fetching SPF record for {domain}: ", str(e))

    # reading domains from a file
def get_domains_from_file(filename):
    lines = []
    with open(filename, 'r') as file:  # , encoding='utf-16'
        for line in file:
            try:
                l, m = line.split(',')
                m = m.strip()
                lines.append(m)
            except Exception as e:
                print(f"Exception {str(e)}, {line}")

        # print(lines)
        return lines
        # return [line.strip() for line in file]




filename = 'domains.txt'

    # usage

domains = get_domains_from_file(filename)
get_spf_record(domains)