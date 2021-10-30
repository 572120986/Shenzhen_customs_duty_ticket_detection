"""
增值税机打发票识别
"""
from numpy.core.defchararray import isdigit

from apphelper.image import union_rbox
import re



class invoice_h:
    """
    海关税票结构化识别
    """

    def __init__(self, result):
        # self.result = union_rbox(result, 0.01)
        self.result = result
        self.N = len(self.result)
        self.res = {}
        self.code()  # 号码
        self.account()  # 发票号码
        self.date()  # 填发日期
        self.price()  # 合计
        self.name()  # 名称
        self.type()  # 类型


  # 账号
    def code(self):
        """

        """
        n = 0
        No = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            n=n+i
            print(str(n)+txt)
            txt = txt.replace(' ', '')
            pattern = re.compile(r'[\u4e00-\u9fa5]')#去除中文
            linee = re.sub(pattern, '', txt)
            linee2 = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])",  "",linee)
            linee3 = re.sub("[M]", "", linee2)
            linee4 = re.sub("[l]", "", linee3)
            linee5 = re.sub("[s]", "", linee4)
            linee5 = re.sub("[I]", "", linee5)
            linee5 = re.sub("[F]", "", linee5)
            linee5 = re.sub("[y]", "", linee5)
            linee5 = re.sub("[ri]", "", linee5)
            if len(linee5) >=11 and linee5.isdigit():
                print("账号:"+linee5)
                res = linee5
                No['account'] = res
                self.res.update(No)
                break

    # 号码
    def account(self):
        """
        识别发票号码
        """
        nu = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            txt = txt.replace(' ', '')
            res = re.findall('(?:(?<!\d)\d{18}-[A-Z]{1,1}\d{2}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{18}/[A-Z]{1,1}\d{2}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{18}[A-Z]{1,1}\d{2}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{18}-[A-Z]{1,2}\d{1}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{18}[A-Z]{1,2}\d{1}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{21}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{18}-\d{3}(?!\d))', txt)
            res += re.findall('(?:(?<!\d)\d{22}(?!\d))', txt)
            if len(res) > 0:
                nu["number"] = res[0].replace('NO.','').replace('No.','').replace('N0.','').replace('N.','').replace('号码.','')
                self.res.update(nu)
                break

    # 名称
    def name(self):
        """
        识别发票号码
        """
        nu = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            txt = txt.replace(' ', '')
            linee4 = re.sub("[l]", "", txt)
            res1 = re.findall('名称[\u4e00-\u9fa5]*', linee4)
            res1 += re.findall('[\u4e00-\u9fa5]*公司', linee4)
            if len(res1) > 0:
                res1=str(res1[0].strip())
                res2=''
                if res1[0:1]=="校":
                    res2=re.sub('校','', res1)
                    nu["名称"] = res2
                elif res1[0:2]=="金库":
                    res2=re.sub('金库', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="苷":
                    res2=re.sub('苷', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="室":
                    res2=re.sub('室','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="率":
                    res2=re.sub('率','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="库":
                    res2 = re.sub('库','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="会":
                    res2 = re.sub('会','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="车":
                    res2=re.sub('车','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="运":
                    res2=re.sub('运', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="闻":
                    res2=re.sub('闻','', res1)
                    nu["名称"] = res2
                elif res1[0:1]=="妃":
                    res2=re.sub('妃', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="裙":
                    res2=re.sub('裙', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="月":
                    res2=re.sub('月', '',res1)
                    nu["名称"] = res2
                elif res1[0:1]=="洵":
                    res2=re.sub('洵', '',res1)
                    nu["名称"] = res2
                elif res1[0:1] == "诈":
                    res2 = re.sub('诈', '', res1)
                    nu["名称"] = res2
                elif res1[0:1] == "审":
                    res2 = re.sub('审', '', res1)
                    nu["名称"] = res2
                elif res1[0:2]=="征库":
                    res2 = re.sub('征库','', res1)
                    nu["名称"] = res2
                elif res1[0:2] == "全库":
                    res2 = re.sub('全库', '', res1)
                    nu["名称"] = res2
                elif res1[0:2] == "会库":
                    res2 = re.sub(' 会库', '', res1)
                    nu["name"] = res2
                else:
                    nu["name"] = res1

                self.res.update(nu)
                break

    # 日期
    def date(self):
        """
        识别开票日期
        """
        da = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            txt = txt.replace(' ', '')
            res1 = re.findall('[0-9]{1,4}年[0-9]{1,2}月[0-9]{1,2}日', txt)
            if len(res1) > 0:
                da["date"] = res1[0]
                self.res.update(da)
                break

    # 合计
    def price(self):
        """
        识别税后价格（小写）
        """
        pri = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            txt2 = txt.replace(' ', '')
            # txt = re.sub("[l]", "", txt2)
            res1 = re.findall('[l]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[￥]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall(r'[\u4e00-\u9fa5]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[￥]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[圣]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[-]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[|]{1,1}\d{1,9}[.]{1,1}\d{1,2}', txt)
            res1 += re.findall('[|]{1,1}[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]{1,1}[0-9]{2,8}[.]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]{1,1}[0-9]{2,8}[,]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]{1,1}[0-9]{2,8}[.]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]{1,1}[A-Za-z]{1,1}[0-9]{2,8}[.]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[A-Za-z]{1,1}[0-9]{2,8}[.]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[A-Za-z]{1,1}[0-9]{2,8}[,]{1,1}[0-9]{1,2}', txt)
            res1 += re.findall('[0-9]{2,8}[.]{1,1}[0-9]{1,2}', txt)
            # res1 += re.findall('[0-9]{1,9}[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]{1,1}[0-9]{1,2}', txt)
            if len(res1) > 0:
                txtres = re.sub(r'[\u4e00-\u9fa5]', '', res1[0])
                linee2 = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", txtres)
                linee3 = re.sub("[A-Za-z]", "", linee2)
                linee3_i=list(linee3)
                linee3_i.insert(-2,'.')
                linee3=''.join(linee3_i)
                pri["price"] = linee3
                self.res.update(pri)
                break
    def type(self):
        """
        识别发票号码
        """
        type = {}
        for i in range(self.N):
            txt = self.result[i]['text'].replace(' ', '')
            txt = txt.replace(' ', '')
            linee4 = re.sub("[l]", "", txt)
            res1 = re.findall('海关[\u4e00-\u9fa5]*', linee4)
            res1 += re.findall('-海关[\u4e00-\u9fa5]*', linee4)
            if len(res1) > 0:
                res1 = str(res1[0].strip())
                type["type"] = res1
                self.res.update(type)
                break









