
import scrapy

class LinkedInPeopleProfileSpider(scrapy.Spider):
    name = "linkedin_people_profile"

    custom_settings = {
        'FEEDS': { 'data/%(name)s_%(time)s.jsonl': { 'format': 'jsonlines',}}
        }

    def start_requests(self):
        profile_list = ['https://au.linkedin.com/in/nehemiahjacob',
'https://au.linkedin.com/in/emma-ai-21531530',
'https://au.linkedin.com/in/nick-h-5497a1232',
'https://au.linkedin.com/in/priyanka-priyadarshini-62b696219',
'https://au.linkedin.com/in/duy-trinh',
'https://au.linkedin.com/in/sneha-pk-pradhan',
'https://au.linkedin.com/in/manveer-singh-a52a44187',
'https://au.linkedin.com/in/addyyeow',
'https://au.linkedin.com/in/chris-marwick-297b56b7',
'https://au.linkedin.com/in/sadman-shafiq',
'https://au.linkedin.com/in/mahdikazemim',
'https://au.linkedin.com/in/jsunster',
'https://au.linkedin.com/in/australian-society-of-biomedical-machine-learning-asbml-43a37b218',
'https://au.linkedin.com/in/ehsanabb',
'https://au.linkedin.com/in/simon-lucey-143425114',
'https://au.linkedin.com/in/luke-smith-1666b416a',
'https://au.linkedin.com/in/harry-stuart',
'https://au.linkedin.com/in/james-bockman-51a81380',
'https://au.linkedin.com/in/yingmingl',
'https://au.linkedin.com/in/camerondgordon',
'https://au.linkedin.com/in/emily-nota-9594a2a6'
'https://au.linkedin.com/in/alex-jenkins-4107074'
'https://au.linkedin.com/in/craig-price-aa452714'
'https://au.linkedin.com/in/nitinsach'
'https://au.linkedin.com/in/kenny-loh-733319a6'
'https://au.linkedin.com/in/arunapattam'
'https://au.linkedin.com/in/hoang-thai-a54a1386'
'https://au.linkedin.com/in/mitchell-west-b1962a108'
'https://au.linkedin.com/in/jchammas'
'https://au.linkedin.com/in/kevin-kw-cheng'
'https://au.linkedin.com/in/centre-for-applied-artificial-intelligence',
 'https://au.linkedin.com/in/stelasolar',
 'https://au.linkedin.com/in/timothy-newnham-14192ba9',
 'https://au.linkedin.com/in/lisabouari',
 'https://au.linkedin.com/in/ian-will-16b2311b3',
 'https://au.linkedin.com/in/griffith-artificial-intelligence-society-39645220a',
 'https://au.linkedin.com/in/sankhya-singh-990b67192',
 'https://au.linkedin.com/in/dalibor-ivkovic-5bb2b27',
 'https://au.linkedin.com/in/ajhepworth',
 'https://au.linkedin.com/in/amelia-poetter']

        for profile in profile_list:
            linkedin_people_url = profile
            yield scrapy.Request(url=linkedin_people_url, callback=self.parse_profile, meta={'profile': profile, 'linkedin_url': linkedin_people_url})

    def parse_profile(self, response):
        item = {}
        item['profile'] = response.meta['profile']
        item['url'] = response.meta['linkedin_url']

        """
            SUMMARY SECTION
        """
        summary_box = response.css("section.top-card-layout")
        item['name'] = summary_box.css("h1::text").get().strip()
        item['description'] = summary_box.css("h2::text").get().strip()

        ## Location
        try:
            item['location'] = summary_box.css('div.top-card__subline-item::text').get()
        except:
            item['location'] = summary_box.css('span.top-card__subline-item::text').get().strip()
            if 'followers' in item['location'] or 'connections' in item['location']:
                item['location'] = ''

        item['followers'] = ''
        item['connections'] = ''

        for span_text in summary_box.css('span.top-card__subline-item::text').getall():
            if 'followers' in span_text:
                item['followers'] = span_text.replace(' followers', '').strip()
            if 'connections' in span_text:
                item['connections'] = span_text.replace(' connections', '').strip()


        """
            ABOUT SECTION
        """
        item['about'] = response.css('section.summary div.core-section-container__content p::text').get(default='')


        """
            EXPERIENCE SECTION
        """
        item['experience'] = []
        experience_blocks = response.css('li.experience-item')
        for block in experience_blocks:
            experience = {}
            ## organisation profile url
            experience['organisation_profile'] = block.css('h4 a::attr(href)').get(default='').split('?')[0]
                
                
            ## location
            experience['location'] = block.css('p.experience-item__location::text').get(default='').strip()
                
                
            ## description
            try:
                experience['description'] = block.css('p.show-more-less-text__text--more::text').get().strip()
            except Exception as e:
                print('experience --> description', e)
                try:
                    experience['description'] = block.css('p.show-more-less-text__text--less::text').get().strip()
                except Exception as e:
                    print('experience --> description', e)
                    experience['description'] = ''
                    
            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = date_ranges[1]
                    experience['duration'] = block.css('span.date-range__duration::text').get()
                elif len(date_ranges) == 1:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = 'present'
                    experience['duration'] = block.css('span.date-range__duration::text').get()
            except Exception as e:
                print('experience --> time ranges', e)
                experience['start_time'] = ''
                experience['end_time'] = ''
                experience['duration'] = ''
            
            item['experience'].append(experience)

        
        """
            EDUCATION SECTION
        """
        item['education'] = []
        education_blocks = response.css('li.education__list-item')
        for block in education_blocks:
            education = {}

            ## organisation
            education['organisation'] = block.css('h3::text').get(default='').strip()


            ## organisation profile url
            education['organisation_profile'] = block.css('a::attr(href)').get(default='').split('?')[0]

            ## course details
            try:
                education['course_details'] = ''
                for text in block.css('h4 span::text').getall():
                    education['course_details'] = education['course_details'] + text.strip() + ' '
                education['course_details'] = education['course_details'].strip()
            except Exception as e:
                print("education --> course_details", e)
                education['course_details'] = ''

            ## description
            education['description'] = block.css('div.education__item--details p::text').get(default='').strip()


         
            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = date_ranges[1]
                elif len(date_ranges) == 1:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = 'present'
            except Exception as e:
                print("education --> time_ranges", e)
                education['start_time'] = ''
                education['end_time'] = ''

            item['education'].append(education)

        yield item
        

        