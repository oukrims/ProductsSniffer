
import requests
import random
import re
import time
import json
from bs4 import BeautifulSoup
from lxml import cssselect
import urllib.request
from Models.products import products


class productSniffer():
   
    # initiate the default configuration
    def __init__(self, base_url, cat_id, cat_name):
        super().__init__()
        self.base_url = base_url
        self.cat_id = cat_id
        self.cat_name = cat_name
        
    # parse the product detail page
    def getproductdetail(self,cat_id, cat_name, num_retries=3):
        IP = productSniffer.get_proxy_ip()
        user_agent = productSniffer.get_user_agent()
        timesleep = random.random() * 5
        current_page = "1"
        page_url = "https://www.aliexpress.com/category/"+cat_id+"/"+cat_name+"/"+current_page+".html"

        try:
            print('Requesting  page ', page_url)
            req = urllib.request.Request(page_url)
            req.add_header('User-Agent', user_agent)
            req.add_header('X-Forwarded-For', IP)
            req.add_header('X-Real-IP', IP)
            req.add_header('Referer', page_url)
            
            # using IP proxy
            proxy_support = urllib.request.ProxyHandler({'http':'http://' + IP + '/'})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
            
            SourceData = urllib.request.urlopen(req).read()
            SourceData = SourceData.decode("utf-8")

            soup = BeautifulSoup(str(SourceData), 'lxml')
            productLists = soup.find_all('li', class_="list-item")
            page_index = int(page_url.split('/')[-1].split('.html')[0])
            Counter = (48 * (page_index - 1) + 1)
            if 'login-home-new' in str(SourceData):
                print('Temperorily blocked ! Wait 10 minutes')
                time.sleep(360)
                productSniffer.getproductdetail(self, "528","batteries", num_retries - 1)
            else:
                product_data = {}
                for eachProduct in productLists:
                    product_data.clear()
                    product_title = eachProduct.find('a', class_="product").get_text().strip().replace('\'', '\'\'')  # get product title, ok
                    product_url = 'https:' + eachProduct.find('a', class_="product").get('href')  # get product url,ok
                    product_id = product_url.split('?')[0].split('/')[-1].split('.')[0]
                    product_prices = eachProduct.select('.value')  # get product unit price, ok
                    product_unit_price = product_prices[0].text.strip().replace('US $', '')
                    product_units = eachProduct.select('.unit')  # get product unit, ok
                    product_unit = product_units[0].text
                    
                   
                    product_data['product_id'] = product_id
                    product_data['product_title'] = product_title
                    product_data['product_url'] = product_url
                    product_data['product_unit_price'] = product_unit_price
                    product_data['product_unit'] = product_unit
                    
                    img_urls = eachProduct.select('img')  # get product image url, ok
                    if len(img_urls) > 1:
                        product_rateimg_url = img_urls[0].get('src')  # get product rating image url, ok
                
                        if img_urls[1].get('image-src') is not None:
                            product_img_url = img_urls[1].get('image-src')
                            product_data['product_img_url'] = product_img_url
                            product_data['product_rateimg_url'] = product_rateimg_url
                            
                        else:
                            product_img_url = img_urls[1].get('src')
                            product_data['product_img_url'] = product_img_url
                            product_data['product_rateimg_url'] = product_rateimg_url
                            
                    else:
                        product_rateimg_url = 'No rating yet'
                        if img_urls[0].get('image-src') is not None:
                            product_img_url = img_urls[0].get('image-src')
                            product_data['product_img_url'] = product_img_url
                            product_data['product_rateimg_url'] = product_rateimg_url
                            
                        else:
                            product_img_url = img_urls[0].get('src')
                            product_data['product_img_url'] = product_img_url
                            product_data['product_rateimg_url'] = product_rateimg_url
                            
                            
                    # get product feedbacks, ok
                    
                    if len(eachProduct.select('.rate-num')) > 0:
                        product_feedback_num = eachProduct.find('a', class_="rate-num").get_text().replace('Feedback(', '').replace(')', '')
                        product_data['product_feedback_num'] = product_feedback_num
                    else:
                        product_feedback_num = 0
                        product_data['product_feedback_num'] = product_feedback_num
                    
                    
                    if len(product_prices) > 1:  # if charge shipping fee, will get the shipping method and shipping price , ok     
                        product_shipping_method = eachProduct.find('dd', class_="price").get_text().split('via')[1].strip().replace('\'', '\'\'')
                        product_shipping_price = product_prices[1].text.replace('US $', '')
                        product_data['product_shipping_method'] = product_shipping_method
                        product_data['product_shipping_price'] = product_shipping_price
                        
                    else:
                        product_shipping_method = 'Freeshipping'
                        product_shipping_price = 0
                        product_data['product_shipping_method'] = product_shipping_method
                        product_data['product_shipping_price'] = product_shipping_price
                        
                    # product rank index on the current page
                    product_page_index = page_index
                    product_rank_index = Counter
                    product_data['product_rank_index'] = product_rank_index
                    product_data['product_page_index'] = product_page_index
                    
                    # check if the product was P4P clicked promoted , ok
                    if len(eachProduct.select('.sponsored')) > 0:
                        product_promoted_status = 'yes'
                        product_data['product_promoted_status'] = product_promoted_status
                        # self.product_sponsors.append('yes')
                    else:
                        product_promoted_status = 'no'
                        product_data['product_promoted_status'] = product_promoted_status
                        # get product sold order numbers, ok
                        product_sold_num =  eachProduct.find('em', title="Total Orders").get_text().replace('Orders  (', '').replace(')', '').strip()
                        product_data['product_sold_num'] = product_sold_num

                        # self.product_sponsors.append('no')
                    
                    
                    product_store_url = 'https:' + eachProduct.find('a', class_="store").get('href')  # get product store url, ok
                    product_store_name = eachProduct.find('a', class_="store").get_text().strip().replace('\'', '\'\'')  # get product Store name, ok
                    
                    product_data['product_store_name'] = product_store_name
                    product_data['product_store_url'] = product_store_url
                    '''
                    Products =  products()
                    inserted_id = Products.addProduct(product_data)
                    print(inserted_id)
                    '''
                    
                    Counter = Counter + 1
                    if Counter  > 47:
                        current_page = int(current_page) + 1

                time.sleep(timesleep)
                
        except urllib.request.URLError as e:
            if num_retries > 0:
                if hasattr(e):
                    print('Error', str(e))
                    res = None
                    return productSniffer.getproductdetail("528","batteries", num_retries - 1)
               
    # get random user-agent
    @staticmethod
    def get_user_agent():
        useragents = ['Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
                     'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
                     'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
                     'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
                     'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
                     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
                     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
                     'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11']

        user_agent = random.choice(useragents)
        return user_agent
    
       
    # get proxy IPs
    @staticmethod
    def get_proxy_ip():
        BaseURL = 'http://falcon.proxyrotator.com:51337/?apiKey=dDnk4sLwyc2H68u3ZMmUTWxNFPV9gCpt&get=true'
        response = requests.get(BaseURL).text
        response = json.loads(response)
        IP = response['proxy']
        return  IP
        
    def error(self):
        pass
    
# test 
base_url = 'https://www.aliexpress.com'
#https://www.aliexpress.com/category/{cat id}/{cat name}/{page}.html?site=glo&g=y&SortType=total_tranpro_desc&needQuery=n&tag=
page_url = 'https://www.aliexpress.com/category/528/batteries/7.html?g=n' 
profinder = productSniffer(base_url,"528","batteries")
profinder.getproductdetail("528","batteries", num_retries=2)



    
