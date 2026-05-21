from django.core.management.base import BaseCommand
from locations.models import District, City, Area


MAHARASHTRA_DATA = {
    'Pune': {
        'code': 'PUN', 'name_mr': 'पुणे', 'name_hi': 'पुणे',
        'cities': {
            'Pune City': {'name_mr': 'पुणे शहर', 'name_hi': 'पुणे शहर', 'areas': [
                ('Kothrud', 'कोथरूड', 'कोथरूड', '411038'),
                ('Shivajinagar', 'शिवाजीनगर', 'शिवाजीनगर', '411005'),
                ('Hadapsar', 'हडपसर', 'हडपसर', '411028'),
                ('Baner', 'बाणेर', 'बाणेर', '411045'),
                ('Wakad', 'वाकड', 'वाकड', '411057'),
                ('Hinjewadi', 'हिंजवडी', 'हिंजवडी', '411057'),
                ('Aundh', 'औंध', 'औंध', '411007'),
                ('Viman Nagar', 'विमाननगर', 'विमाननगर', '411014'),
                ('Koregaon Park', 'कोरेगाव पार्क', 'कोरेगाव पार्क', '411001'),
                ('Pimpri', 'पिंपरी', 'पिंपरी', '411018'),
            ]},
            'Pimpri-Chinchwad': {'name_mr': 'पिंपरी-चिंचवड', 'name_hi': 'पिंपरी-चिंचवड', 'areas': [
                ('Chinchwad', 'चिंचवड', 'चिंचवड', '411033'),
                ('Akurdi', 'आकुर्डी', 'आकुर्डी', '411035'),
                ('Bhosari', 'भोसरी', 'भोसरी', '411026'),
                ('Kalewadi', 'कालेवाडी', 'कालेवाडी', '411033'),
                ('Nigdi', 'निगडी', 'निगडी', '411044'),
            ]},
            'Baramati': {'name_mr': 'बारामती', 'name_hi': 'बारामती', 'areas': [
                ('Baramati City', 'बारामती शहर', 'बारामती शहर', '413102'),
                ('Bhigwan', 'भिगवण', 'भिगवण', '413105'),
            ]},
            'Lonavala': {'name_mr': 'लोणावळा', 'name_hi': 'लोनावला', 'areas': [
                ('Lonavala City', 'लोणावळा शहर', 'लोनावला शहर', '410401'),
                ('Khandala', 'खंडाळा', 'खंडाला', '410301'),
            ]},
        }
    },
    'Mumbai Suburban': {
        'code': 'MUM', 'name_mr': 'मुंबई उपनगर', 'name_hi': 'मुंबई उपनगर',
        'cities': {
            'Andheri': {'name_mr': 'अंधेरी', 'name_hi': 'अंधेरी', 'areas': [
                ('Andheri East', 'अंधेरी पूर्व', 'अंधेरी पूर्व', '400069'),
                ('Andheri West', 'अंधेरी पश्चिम', 'अंधेरी पश्चिम', '400058'),
                ('Jogeshwari', 'जोगेश्वरी', 'जोगेश्वरी', '400060'),
                ('Versova', 'वर्सोवा', 'वर्सोवा', '400061'),
            ]},
            'Borivali': {'name_mr': 'बोरिवली', 'name_hi': 'बोरीवली', 'areas': [
                ('Borivali East', 'बोरिवली पूर्व', 'बोरीवली पूर्व', '400066'),
                ('Borivali West', 'बोरिवली पश्चिम', 'बोरीवली पश्चिम', '400092'),
                ('Kandivali', 'कांदिवली', 'कांदिवली', '400067'),
                ('Malad', 'मालाड', 'मालाड', '400064'),
            ]},
            'Thane': {'name_mr': 'ठाणे', 'name_hi': 'ठाणे', 'areas': [
                ('Thane West', 'ठाणे पश्चिम', 'ठाणे पश्चिम', '400601'),
                ('Thane East', 'ठाणे पूर्व', 'ठाणे पूर्व', '400603'),
                ('Ghodbunder Road', 'घोडबंदर रोड', 'घोड़बंदर रोड', '400615'),
                ('Kalwa', 'कळवा', 'कल्वा', '400605'),
            ]},
            'Navi Mumbai': {'name_mr': 'नवी मुंबई', 'name_hi': 'नवी मुंबई', 'areas': [
                ('Vashi', 'वाशी', 'वाशी', '400703'),
                ('Nerul', 'नेरुळ', 'नेरुल', '400706'),
                ('Kharghar', 'खारघर', 'खारघर', '410210'),
                ('Panvel', 'पनवेल', 'पनवेल', '410206'),
                ('Belapur', 'बेलापूर', 'बेलापुर', '400614'),
            ]},
        }
    },
    'Nagpur': {
        'code': 'NGP', 'name_mr': 'नागपूर', 'name_hi': 'नागपुर',
        'cities': {
            'Nagpur City': {'name_mr': 'नागपूर शहर', 'name_hi': 'नागपुर शहर', 'areas': [
                ('Sitabuldi', 'सीताबर्डी', 'सीताबर्डी', '440012'),
                ('Dharampeth', 'धरमपेठ', 'धर्मपेठ', '440010'),
                ('Sadar', 'सदर', 'सदर', '440001'),
                ('Ramdaspeth', 'रामदासपेठ', 'रामदासपेठ', '440010'),
                ('Manish Nagar', 'मानीश नगर', 'मानीश नगर', '440015'),
                ('Mankapur', 'मानकापूर', 'मानकापुर', '440030'),
                ('Kamptee', 'कामटी', 'कामटी', '441001'),
            ]},
            'Wardha': {'name_mr': 'वर्धा', 'name_hi': 'वर्धा', 'areas': [
                ('Wardha City', 'वर्धा शहर', 'वर्धा शहर', '442001'),
                ('Sevagram', 'सेवाग्राम', 'सेवाग्राम', '442102'),
            ]},
            'Yavatmal': {'name_mr': 'यवतमाळ', 'name_hi': 'यवतमाल', 'areas': [
                ('Yavatmal City', 'यवतमाळ शहर', 'यवतमाल शहर', '445001'),
            ]},
        }
    },
    'Nashik': {
        'code': 'NSK', 'name_mr': 'नाशिक', 'name_hi': 'नासिक',
        'cities': {
            'Nashik City': {'name_mr': 'नाशिक शहर', 'name_hi': 'नासिक शहर', 'areas': [
                ('Panchavati', 'पंचवटी', 'पंचवटी', '422003'),
                ('Nashik Road', 'नाशिक रोड', 'नासिक रोड', '422101'),
                ('Gangapur Road', 'गंगापूर रोड', 'गंगापुर रोड', '422013'),
                ('Cidco', 'सिडको', 'सिडको', '422009'),
                ('Satpur', 'सातपूर', 'सातपुर', '422007'),
                ('Ambad', 'अंबड', 'अंबड', '422010'),
            ]},
            'Malegaon': {'name_mr': 'मालेगाव', 'name_hi': 'मालेगांव', 'areas': [
                ('Malegaon Camp', 'मालेगाव कॅम्प', 'मालेगांव कैम्प', '423203'),
                ('Malegaon City', 'मालेगाव शहर', 'मालेगांव शहर', '423203'),
            ]},
            'Igatpuri': {'name_mr': 'इगतपुरी', 'name_hi': 'इगतपुरी', 'areas': [
                ('Igatpuri Town', 'इगतपुरी गाव', 'इगतपुरी नगर', '422403'),
            ]},
        }
    },
    'Aurangabad': {
        'code': 'AUR', 'name_mr': 'औरंगाबाद', 'name_hi': 'औरंगाबाद',
        'cities': {
            'Aurangabad City': {'name_mr': 'औरंगाबाद शहर', 'name_hi': 'औरंगाबाद शहर', 'areas': [
                ('Cidco', 'सिडको', 'सिडको', '431003'),
                ('Garkheda', 'गारखेडा', 'गारखेडा', '431009'),
                ('Cantonment', 'कॅन्टोनमेंट', 'कैंटोनमेंट', '431002'),
                ('Osmanpura', 'उस्मानपुरा', 'उस्मानपुरा', '431005'),
                ('Begumpura', 'बेगमपुरा', 'बेगमपुरा', '431004'),
                ('Waluj', 'वाळूज', 'वालुज', '431136'),
            ]},
            'Jalna': {'name_mr': 'जालना', 'name_hi': 'जालना', 'areas': [
                ('Jalna City', 'जालना शहर', 'जालना शहर', '431203'),
            ]},
            'Beed': {'name_mr': 'बीड', 'name_hi': 'बीड', 'areas': [
                ('Beed City', 'बीड शहर', 'बीड शहर', '431122'),
            ]},
        }
    },
    'Kolhapur': {
        'code': 'KLP', 'name_mr': 'कोल्हापूर', 'name_hi': 'कोल्हापुर',
        'cities': {
            'Kolhapur City': {'name_mr': 'कोल्हापूर शहर', 'name_hi': 'कोल्हापुर शहर', 'areas': [
                ('Shivaji Peth', 'शिवाजी पेठ', 'शिवाजी पेठ', '416012'),
                ('Rajarampuri', 'राजारामपुरी', 'राजारामपुरी', '416008'),
                ('Tarabai Park', 'ताराबाई पार्क', 'ताराबाई पार्क', '416003'),
                ('Laxmipuri', 'लक्ष्मीपुरी', 'लक्ष्मीपुरी', '416002'),
                ('Kasba Bawada', 'कसबा बावडा', 'कसबा बावडा', '416006'),
            ]},
            'Ichalkaranji': {'name_mr': 'इचलकरंजी', 'name_hi': 'इचलकरंजी', 'areas': [
                ('Ichalkaranji City', 'इचलकरंजी शहर', 'इचलकरंजी शहर', '416115'),
            ]},
            'Sangli': {'name_mr': 'सांगली', 'name_hi': 'सांगली', 'areas': [
                ('Sangli City', 'सांगली शहर', 'सांगली शहर', '416416'),
                ('Miraj', 'मिरज', 'मिरज', '416410'),
            ]},
        }
    },
    'Solapur': {
        'code': 'SLP', 'name_mr': 'सोलापूर', 'name_hi': 'सोलापुर',
        'cities': {
            'Solapur City': {'name_mr': 'सोलापूर शहर', 'name_hi': 'सोलापुर शहर', 'areas': [
                ('North Solapur', 'उत्तर सोलापूर', 'उत्तर सोलापुर', '413006'),
                ('South Solapur', 'दक्षिण सोलापूर', 'दक्षिण सोलापुर', '413007'),
                ('Hotgi Road', 'होटगी रोड', 'होटगी रोड', '413003'),
                ('Vijapur Road', 'विजापूर रोड', 'विजापुर रोड', '413004'),
                ('Akkalkot Road', 'अक्कलकोट रोड', 'अक्कलकोट रोड', '413109'),
            ]},
            'Pandharpur': {'name_mr': 'पंढरपूर', 'name_hi': 'पंढरपुर', 'areas': [
                ('Pandharpur City', 'पंढरपूर शहर', 'पंढरपुर शहर', '413304'),
            ]},
        }
    },
    'Thane': {
        'code': 'THN', 'name_mr': 'ठाणे', 'name_hi': 'ठाणे',
        'cities': {
            'Thane City': {'name_mr': 'ठाणे शहर', 'name_hi': 'ठाणे शहर', 'areas': [
                ('Kopri', 'कोपरी', 'कोपरी', '400603'),
                ('Vasant Vihar', 'वसंत विहार', 'वसंत विहार', '400610'),
                ('Hiranandani Estate', 'हिरानंदानी इस्टेट', 'हिरानंदानी एस्टेट', '400607'),
                ('Majiwada', 'माजीवाडा', 'माजीवाडा', '400601'),
            ]},
            'Kalyan': {'name_mr': 'कल्याण', 'name_hi': 'कल्याण', 'areas': [
                ('Kalyan East', 'कल्याण पूर्व', 'कल्याण पूर्व', '421306'),
                ('Kalyan West', 'कल्याण पश्चिम', 'कल्याण पश्चिम', '421301'),
                ('Dombivli', 'डोंबिवली', 'डोंबिवली', '421201'),
                ('Ulhasnagar', 'उल्हासनगर', 'उल्हासनगर', '421003'),
            ]},
            'Badlapur': {'name_mr': 'बदलापूर', 'name_hi': 'बदलापुर', 'areas': [
                ('Badlapur East', 'बदलापूर पूर्व', 'बदलापुर पूर्व', '421503'),
                ('Ambernath', 'अंबरनाथ', 'अंबरनाथ', '421501'),
            ]},
        }
    },
    'Ratnagiri': {
        'code': 'RTG', 'name_mr': 'रत्नागिरी', 'name_hi': 'रत्नागिरी',
        'cities': {
            'Ratnagiri City': {'name_mr': 'रत्नागिरी शहर', 'name_hi': 'रत्नागिरी शहर', 'areas': [
                ('Ratnagiri Town', 'रत्नागिरी गाव', 'रत्नागिरी नगर', '415612'),
                ('Mirya', 'मिर्या', 'मिर्या', '415639'),
                ('Bhatye', 'भाट्ये', 'भाट्ये', '415639'),
            ]},
            'Chiplun': {'name_mr': 'चिपळूण', 'name_hi': 'चिपलून', 'areas': [
                ('Chiplun City', 'चिपळूण शहर', 'चिपलून शहर', '415605'),
            ]},
            'Rajapur': {'name_mr': 'राजापूर', 'name_hi': 'राजापुर', 'areas': [
                ('Rajapur Town', 'राजापूर गाव', 'राजापुर नगर', '416702'),
            ]},
        }
    },
    'Satara': {
        'code': 'SAT', 'name_mr': 'सातारा', 'name_hi': 'सातारा',
        'cities': {
            'Satara City': {'name_mr': 'सातारा शहर', 'name_hi': 'सातारा शहर', 'areas': [
                ('Satara Camp', 'सातारा कॅम्प', 'सातारा कैम्प', '415001'),
                ('Powai Naka', 'पोवई नाका', 'पोवई नाका', '415001'),
                ('Shivaji Road', 'शिवाजी रोड', 'शिवाजी रोड', '415001'),
            ]},
            'Karad': {'name_mr': 'कराड', 'name_hi': 'कराड', 'areas': [
                ('Karad City', 'कराड शहर', 'कराड शहर', '415110'),
            ]},
            'Mahabaleshwar': {'name_mr': 'महाबळेश्वर', 'name_hi': 'महाबलेश्वर', 'areas': [
                ('Mahabaleshwar Town', 'महाबळेश्वर गाव', 'महाबलेश्वर नगर', '412806'),
                ('Panchgani', 'पाचगणी', 'पाचगनी', '412805'),
            ]},
        }
    },
}


class Command(BaseCommand):
    help = 'Seed Maharashtra districts, cities, and areas'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Maharashtra location data...')
        created_districts = 0
        created_cities = 0
        created_areas = 0

        for district_name, district_data in MAHARASHTRA_DATA.items():
            district, d_created = District.objects.get_or_create(
                code=district_data['code'],
                defaults={
                    'name_en': district_name,
                    'name_mr': district_data['name_mr'],
                    'name_hi': district_data['name_hi'],
                    'is_active': True,
                }
            )
            if d_created:
                created_districts += 1
                self.stdout.write(f'  Created district: {district_name}')

            for city_name, city_data in district_data['cities'].items():
                city, c_created = City.objects.get_or_create(
                    district=district,
                    name_en=city_name,
                    defaults={
                        'name_mr': city_data['name_mr'],
                        'name_hi': city_data['name_hi'],
                        'is_active': True,
                    }
                )
                if c_created:
                    created_cities += 1

                for area_data in city_data['areas']:
                    area_en, area_mr, area_hi, pin = area_data
                    area, a_created = Area.objects.get_or_create(
                        city=city,
                        name_en=area_en,
                        defaults={
                            'name_mr': area_mr,
                            'name_hi': area_hi,
                            'pin_code': pin,
                            'is_active': True,
                        }
                    )
                    if a_created:
                        created_areas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created_districts} districts, {created_cities} cities, {created_areas} areas.'
        ))
