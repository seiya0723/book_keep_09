from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from django.db.models.functions import TruncMonth
from django.db.models import Count,Sum


from .models import Category,Balance
from .forms import CategoryForm,BalanceForm,YearMonthForm

import datetime


#↓追加
from django.contrib import messages



class IndexView(LoginRequiredMixin,View):
    
    #日ごとの収支計算し返却する。
    def calc(self, balances):

        today       = ""
        before_day  = ""

        day_balances = []
        dic         = { "day":"","income":0,"spending":0 }

        for balance in balances:
            today   = str(balance.pay_date.day)

            #前回のループと日付不一致の時、アペンドして新規作成
            if today != before_day:

                #初期状態ではない場合のみアペンド
                if dic["day"] != "":
                    day_balances.append(dic)

                dic         = { "day":"","income":0,"spending":0 }
                dic["day"]  = today

            if balance.category.income:
                dic["income"] += balance.value
            else:
                dic["spending"] += balance.value

            before_day  = today

        day_balances.append(dic)
        print(day_balances)

        return day_balances

    def get(self, request, *args, **kwargs):

        context     = {}
        context["categories"]  = Category.objects.filter(user=request.user.id).order_by("income")

        form    = YearMonthForm(request.GET)

        cleaned_month   = None
        cleaned_year    = None

        #指定された年月のデータを取得。指定がない・誤りがある場合は今月のデータを取得。
        if form.is_valid():
            cleaned_data    = form.clean()

            print(cleaned_data["month"])
            print(cleaned_data["year"])

            cleaned_month   = cleaned_data["month"]
            cleaned_year    = cleaned_data["year"]

            dt  = datetime.datetime(year=cleaned_data["year"],month=cleaned_data["month"],day=1)

            context["balances"]     = Balance.objects.filter(pay_date__year=cleaned_data["year"],pay_date__month=cleaned_data["month"],user=request.user.id).order_by("pay_date")

        else:
            #今月の初日を手に入れる。
            dt  = datetime.datetime.now()
            dt  = dt.replace(day=1)

            context["balances"]     = Balance.objects.filter(pay_date__year=dt.year,pay_date__month=dt.month,user=request.user.id).order_by("pay_date")

        #TODO:このinit_dtは書き換えしない
        init_dt = dt

        #最新と最古のデータを取得
        oldest_balance  = Balance.objects.order_by("pay_date").first()
        newest_balance  = Balance.objects.order_by("-pay_date").first()

        #ここで存在していれば最古と最新の日付を入手。無い場合はそれぞれ今日の日付を指定
        if oldest_balance:
            oldest_pay_date   = oldest_balance.pay_date
        else:
            oldest_pay_date   = datetime.date.today()

        if newest_balance:
            newest_pay_date   = newest_balance.pay_date
        else:
            newest_pay_date   = datetime.date.today()

        #年リストを作り、Selectタグを作る。
        year_list   = []

        oldest_year = oldest_pay_date.year
        newest_year = newest_pay_date.year

        if cleaned_year != None:
            if cleaned_year <= oldest_pay_date.year:
                oldest_year = cleaned_year
            elif newest_pay_date.year <= cleaned_year:
                newest_year = cleaned_year


        """
        for i in range(oldest_year,newest_year+1,1):
            year_list.append(i)
        """
        #年表示新しい順
        for i in range(newest_year,oldest_year-1,-1):
            year_list.append(i)


        context["year_list"]    = year_list
        context["month"]        = dt.month
        context["year"]         = dt.year

        print(oldest_pay_date)
        print(newest_pay_date)

        #カレンダーに合わせ、日ごとの収支を計算する
        day_balances    = self.calc(context["balances"])

        #今月を手に入れる
        month       = dt.month

        #month_dateはweek_dateのリスト、week_dateは日付のリスト
        month_date  = []
        week_date   = []

        #最終的に作られるmonth_dateのイメージ。このように複数のweek_dateを含む。月の最初が日曜日ではない場合、必要な数だけ空欄をアペンドしておく
        """
        [ ['  ', '  ', '1 ', '2 ', '3 ', '4 ', '5 '],
          ['6 ', '7 ', '8 ', '9 ', '10', '11', '12'],
          ['13', '14', '15', '16', '17', '18', '19'],
          ['20', '21', '22', '23', '24', '25', '26'],
          ['27', '28', '29', '30']
          ]

          [ {"dt":'6 ',"income":3000,"spending":600 }, '7 ', '8 ', '9 ', '10', '11', '12'],
        """

        #一日ずつずらしてweek_dateにアペンドする。
        #datetimeのオブジェクトは .weekday() で数値化した曜日が出力される(月曜日が0、日曜日が6)

        #日曜日以外の場合、空欄を追加する。
        if dt.weekday() != 6:
            for i in range(dt.weekday()+1):
                week_date.append("")

        #1日ずつ追加して月が変わったらループ終了
        while month == dt.month:
            
            #TODO:ここで辞書型をアペンド(日付、収入の合計、支出の合計)
            dic = {"day":str(dt.day),"income":0,"spending":0 }

            flag    = False
            for day_balance in day_balances:
                if dic["day"] == day_balance["day"]:
                    week_date.append(day_balance)
                    flag    = True
                    break

            if not flag:
                week_date.append(dic)

            #1日追加する
            dt  = dt + datetime.timedelta(days=1)

            #週末になるたびに追加する。
            if dt.weekday() == 6:
                month_date.append(week_date)
                week_date   = []

        #一ヶ月の最終週を追加する。
        if dt.weekday() != 6:
            month_date.append(week_date)

        context["month_date"]   = month_date


        #TODO:カテゴリごとのデータを集計する。

        #まずアクセスしたユーザーのカテゴリを取得。
        categories  = Category.objects.filter(user=request.user.id).order_by("income")
        

        category_of_balances    = []

        #カテゴリごとの計算(投稿者であり、指定した年月で絞り込む)
        for category in categories:
            print(init_dt.year)
            print(init_dt.month)
            balances    = Balance.objects.filter(pay_date__year=init_dt.year, pay_date__month=init_dt.month, user=request.user.id, category=category.id)

            total       = 0
            for balance in balances:
                total += balance.value
            
            dic = {}
            dic["income"]   = category.income
            dic["category"] = category.name
            dic["total"]    = total

            data            = dic.copy()
            category_of_balances.append(data)

        context["category_of_balances"] = category_of_balances


        context["monthly_income"]   = Balance.objects.filter(user=request.user.id,category__income=True).annotate(date=TruncMonth("pay_date")).values("date").annotate(count=Count("id"),amount=Sum("value")).values("date","amount", "count").order_by("-date")
        context["monthly_spending"] = Balance.objects.filter(user=request.user.id,category__income=False).annotate(date=TruncMonth("pay_date")).values("date").annotate(count=Count("id"),amount=Sum("value")).values("date","amount", "count").order_by("-date")


        
        #TODO:今月の支出と収入を計算する(今月の自分が投稿したデータで、.aggregate()とSumを使用することで、指定したフィールドの合計値を算出できる。)

        this_month_income = Balance.objects.filter(user=request.user.id, category__income=True, pay_date__year=init_dt.year, pay_date__month=init_dt.month).aggregate(Sum("value"))
        context["this_month_income"] = this_month_income["value__sum"]
        

        this_month_spending = Balance.objects.filter(user=request.user.id, category__income=False, pay_date__year=init_dt.year, pay_date__month=init_dt.month).aggregate(Sum("value"))
        context["this_month_spending"] = this_month_spending["value__sum"]


        this_year_income = Balance.objects.filter(user=request.user.id, category__income=True, pay_date__year=init_dt.year).aggregate(Sum("value"))
        this_year_spending = Balance.objects.filter(user=request.user.id, category__income=False, pay_date__year=init_dt.year).aggregate(Sum("value"))

        #Noneであるにもかかわらず演算をしている。
        if not this_year_income["value__sum"]:
            this_year_income["value__sum"] = 0
            
        if not this_year_spending["value__sum"]:
            this_year_spending["value__sum"] = 0

        print( init_dt.year , "年の収支は", this_year_income["value__sum"] - this_year_spending["value__sum"] ,"円です。")



        month_list  = []
        for i in range(1,13):
            this_month_income = Balance.objects.filter(user=request.user.id, category__income=True, pay_date__year=init_dt.year, pay_date__month=i).aggregate(Sum("value"))
            this_month_spending = Balance.objects.filter(user=request.user.id, category__income=False, pay_date__year=init_dt.year, pay_date__month=i).aggregate(Sum("value"))

            if not this_month_income["value__sum"]:
                this_month_income["value__sum"] = 0
                
            if not this_month_spending["value__sum"]:
                this_month_spending["value__sum"] = 0

            dic = {}
            dic["month"]    = str(i)
            dic["value"]    = this_month_income["value__sum"] - this_month_spending["value__sum"]
            month_list.append(dic)

        print(month_list)

        context["month_list"] = month_list


        income_all_sum = Balance.objects.filter(user=request.user.id,category__income=True).aggregate(Sum("value"))
        spending_all_sum = Balance.objects.filter(user=request.user.id,category__income=False).aggregate(Sum("value"))

        #Noneであるにもかかわらず演算をしている。
        if not income_all_sum["value__sum"]:
            income_all_sum["value__sum"] = 0
                    
        if not spending_all_sum["value__sum"]:
            spending_all_sum["value__sum"] = 0

        print(income_all_sum["value__sum"] - spending_all_sum["value__sum"])

        context["income_all_sum"]  =  income_all_sum
        context["spending_all_sum"]  =  spending_all_sum
        context["all_sum"]  =  income_all_sum["value__sum"] - spending_all_sum["value__sum"]



        #先月と来月のリンクを作る
        if init_dt.month == 12: 
            #来月の計算はyearを1追加、monthを1にする。先月はそのまま1減らす。
            next_month  = "?year=" + str(init_dt.year + 1) + "&month=" + str(1)
            prev_month  = "?year=" + str(init_dt.year) + "&month=" + str(init_dt.month -1) 

        elif init_dt.month == 1:
            #先月の計算はyearを1減らす、monthを12にする。来月はそのまま1追加。
            next_month  = "?year=" + str(init_dt.year) + "&month=" + str(init_dt.month + 1)
            prev_month  = "?year=" + str(init_dt.year - 1) + "&month=" + str(12)

        else:
            #来月、先月それぞれ1追加、1減らすだけでいい
            next_month  = "?year=" + str(init_dt.year) + "&month=" + str(init_dt.month + 1)
            prev_month  = "?year=" + str(init_dt.year) + "&month=" + str(init_dt.month - 1)

        context["next_month"]   = next_month
        context["prev_month"]   = prev_month


        return render(request,"finance/index.html",context)


    def post(self, request, *args, **kwargs):
        
        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        form    = BalanceForm(copied)

        if form.is_valid():
            #TODO:このようにmessagesにメッセージをセットする。
            messages.success(request, "収支を反映しました")
            form.save()
        else:
            messages.error(request, "収支を反映できませんでした")


        return redirect("finance:index")

index   = IndexView.as_view()


class CategoryView(View):

    def get(self, request, pk, *args, **kwargs):
        return redirect("finance:index")

    def post(self, request, *args, **kwargs):

        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        form    = CategoryForm(copied)

        if form.is_valid():
            messages.success(request, "カテゴリを追加しました")
            form.save()
        else:
            
            messages.error(request, "カテゴリを追加できませんでした" )
            # messages.error(request, form.errors)

        return redirect("finance:index")

category    = CategoryView.as_view()


#カテゴリ編集(ログインユーザー専用)
class CategoryEditView(LoginRequiredMixin,View):

    def get(self, request, pk, *args, **kwargs):
        return redirect("finance:index")

    def post(self, request, pk, *args, **kwargs):

        instance    = Category.objects.filter(id=pk,user=request.user.id).first()

        if not instance:
            messages.error(request, "カテゴリを編集できませんでした")
            return redirect("finance:index")


        copied          = request.POST.copy()
        copied["user"]  = request.user.id 


        formset     = CategoryForm(copied, instance=instance)

        if formset.is_valid():
            messages.success(request, "カテゴリを編集しました")
            formset.save()
        else:
            print(formset.errors)
            messages.error(request, "カテゴリを編集できませんでした")

        return redirect("finance:index")

category_edit   = CategoryEditView.as_view()


#カテゴリ削除(ログインユーザー専用)
class CategoryDeleteView(LoginRequiredMixin,View):

    def get(self, request, pk, *args, **kwargs):

        return redirect("finance:index")

    def post(self, request, pk, *args, **kwargs):

        category    = Category.objects.filter(id=pk,user=request.user.id).first()

        if category:
            category.delete()
            messages.success(request, "カテゴリを削除しました")
        else:
            messages.error(request, "カテゴリを削除できませんでした")

        return redirect("finance:index")

category_delete = CategoryDeleteView.as_view()


class BalanceDeleteView(LoginRequiredMixin,View):

    def post(self, request, pk, *args, **kwargs):

        balance = Balance.objects.filter(id=pk).first()

        if balance.user.id != request.user.id:
            messages.success(request, "収支を削除できませんでした")
            return redirect("finance:index")

        balance.delete()
        messages.success(request, "収支を削除しました")

        return redirect("finance:index")

balance_delete  = BalanceDeleteView.as_view()