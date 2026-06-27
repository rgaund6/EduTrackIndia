from django.core.management.base import BaseCommand
from accounts.models import Institute


DATA = [
    ["Pre-Primary Schools", "Hello Kids - Millennium Preschool, Palghar, Maharashtra", "Yashwant Shrusti Rd, Khaira, Boisar, Maharashtra 401501.", "https://www.hellokids.co.in/", "09975506900"],
    ["Pre-Primary Schools", "Shree Ganesh Pre-School", "Saidham, Saravali, Boisar–Palghar Road, Boisar 401501.", "https://shreeganeshschool.co.in/", "09923499314"],
    ["Pre-Primary Schools", "Little Angel Pre School", "Ostwal Bypass, Cidco Colony, Boisar 401506.", "", "09867835227"],
    ["Pre-Primary Schools", "Anandi Gopal Nursery And School Rooprajat Park Betegoan", "Betegaon, Boisar 401501.", "", "09423027256"],
    ["Pre-Primary Schools", "Little Footsteps Preschool and Primary School", "Sainath Nagar, Boisar 401501.", "", "08806862181"],

    ["Primary to Higher Secondary", "St. John International School", "Manor–Palghar Road, Palghar 401404.", "https://www.sjis.edu.in/", "02525297072"],
    ["Primary to Higher Secondary", "Sundaram Central School Palghar", "Mahim Road, Vajulsar, Palghar 401404.", "https://www.sundaramcentralschool.com/", "07020194840"],
    ["Primary to Higher Secondary", "Sacred Heart High School, Palghar", "Vishnu Nagar, Palghar 401404.", "", "07028850321"],
    ["Primary to Higher Secondary", "Sir J. P. International School, Palghar", "Haranwadi Road, Mahim Road, Palghar 401402.", "", "07083061817"],
    ["Primary to Higher Secondary", "Twinkle Star English High School", "Devisha Road, Juna Palghar 401404.", "https://twinklestarenglishschool.in/", "07066582606"],
    ["Primary to Higher Secondary", "Deep Global School and Junior College", "Saravali, Boisar. Website available through Deep Campus.", "https://deepcampus.org/index.html", "07030996452"],
    ["Primary to Higher Secondary", "Chinmaya International Vidyalaya", "P-125, Warangade, Maan, Boisar 401501.", "https://chinmayainternationalvidyalaya.com/", "09168474791"],
    ["Primary to Higher Secondary", "Viraj International School", "Boisar West, Palghar District.", "https://school.careers360.com/schools/viraj-international-school-boisar-west-palghar", "08554998833"],
    ["Primary to Higher Secondary", "Shanti Ratan Vidya Mandir & Junior College", "Boisar 401501.", "", "08550970330"],
    ["Primary to Higher Secondary", "Mumbai Public School", "New Dhandi Pada, Near Raily Way Station, Boisar East, Boisar, Palghar-401501, Maharashtra", "", ""],
    ["Primary to Higher Secondary", "Shri Raghuveer School And Jr College", "Boisar, Palghar-401501, Maharashtra", "https://raghubirschool.in/", "08097879774"],
    ["Primary to Higher Secondary", "Rahul International School", "Shop No 9 & 10, Sai Jayshree Appartment, Boisar, Palghar-401501, Maharashtra", "https://ris.education/campuses/mumbai/boisar-cbse/", ""],
    ["Primary to Higher Secondary", "Don Bosco School", "Near State Bank Of India, BOISAR- TARAPUR Road, Boisar, Palghar-401501, Maharashtra", "http://donboscoboisar.com/", "09096918987"],
    ["Primary to Higher Secondary", "St Francis School Boisar", "Boisar Road, Boisar, Palghar-401501, Maharashtra", "", "07262898901"],
    ["Primary to Higher Secondary", "Swami Vivekanand High School And Junior College Boisar", "Kolavade Road, Boisar, Palghar-401501, Maharashtra", "", ""],
    ["Primary to Higher Secondary", "C T E S English Medium School", "Midc Staff Colony, Boisar, Palghar-401501, Maharashtra", "", ""],
    ["Primary to Higher Secondary", "Atomic Energy Central School Number 1 Boisar", "Taps Colony, Boisar, Palghar-401501, Maharashtra", "", "02525264004"],
    ["Primary to Higher Secondary", "Chhanakya The Global School For Intellectual", "Dhansar, Anand Vridhashram, New Satpati Road, Kuldeep Nagar, Palghar-401404, Maharashtra", "https://www.chanakyatheglobalschool.com/", "09730390599"],

    ["Colleges", "Sonopant Dandekar Shikshan Mandali (SDSM) College", "College Road, Tembhode, Palghar 401404.", "http://sdsmcollege.com/", ""],
    ["Colleges", "St. John College of Engineering and Management", "Vevoor, Palghar 401404.", "https://sjcem.edu.in/", "02525297279"],
    ["Colleges", "St. John College of Humanities and Sciences", "Vevoor, Palghar 401404.", "https://www.sjchs.edu.in/", "02525297071"],
    ["Colleges", "St. John Technical Education Campus", "Old Manor Road, Vevoor, Palghar 401404.", "https://aldel.in/", "07387203232"],
    ["Colleges", "National College", "Vishnu Nagar, Palghar 401404.", "https://nationalcollege.in/", "08068507627"],
    ["Colleges", "Deep's Degree College", "Deep Education Campus, Boisar.", "https://deepcampus.org/institutions.html", "09225138107"],
    ["Colleges", "Theem College of Engineering", "Boisar, Palghar District.", "https://theemcoe.org/", "02525284909"],
]


class Command(BaseCommand):
    help = "Import full Boisar school and college data"

    def handle(self, *args, **kwargs):
        created = 0
        updated = 0

        for category, name, address, website, contact in DATA:
            obj, was_created = Institute.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "address": address,
                    "website": website,
                    "contact_number": contact,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Full Boisar data imported. Created: {created}, Updated: {updated}"
            )
        )