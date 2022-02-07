window.addEventListener("load" , function (){
    draw_pie("income");
    draw_pie("spending");

    draw_bar( x=".month_list_month", y=".month_list_value", canvas="month_list_graph" );
});

function draw_pie(target){

    let elem_categories = $("." + target + "_category");
    let elem_totals     = $("." + target + "_total");

    let categories      = [];
    let totals          = [];

    //jQueryで手に入れた要素をループする。(※この時取り出した要素はjQueryのオブジェクトではない点に注意)
    //カテゴリ名と金額をそれぞれリストに格納(金額は円とカンマを消して、数値型に仕立てる)
    for (let c of elem_categories){
        categories.push(c.innerText);
    }
    for (let t of elem_totals){
        totals.push(Number(t.innerText.replace(",","").replace("円","")));
    }

    console.log(categories);
    console.log(totals);
    
    //色作成(収入の場合は緑系、支出の場合は赤系)
    let colors  = []
    var rgb     = 255;
    var rb      = 100;
    var gb      = 0;
    var minus   = 255/categories.length;
    
    if (target == "income"){
        for (let c of categories){
            colors.push("rgb(0,"  + String(rgb)+ "," + String(rb) +")");
            rgb -= minus;
            rb  -= minus;
        }
    }
    else{
        for (let c of categories){
            colors.push("rgb(" + String(rgb)+ ",0,"+ String(gb) +")");
            rgb -= minus;
            gb  += (minus*0.4);
        }
    }

    //描画
    const ctx = document.getElementById("category_graph_" + target ).getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: totals,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        // options: {
        //     scales: {
        //         y: {
        //             beginAtZero: true,
        //             type:"linear",
        //         },
        //         x: {
        //             beginAtZero: true,
        //             type:"linear",
        //         }
        //     }
        // }
    });
    //scaleの指定でグラフの方眼を描画できる
    //https://www.chartjs.org/docs/3.3.2/axes/

    //目盛の値のみを削除する方法は無い。
    //http://www.kogures.com/hitoshi/javascript/chartjs/scale-label.html

}


function draw_bar(x,y,canvas){

    let elem_x  = $(x);
    let elem_y  = $(y);
    
    let x_list  = [];
    let y_list  = [];

    for (let ex of elem_x){
        x_list.push(ex.innerText);
    }
    for (let ey of elem_y){
        y_list.push(Number(ey.innerText.replace(",","").replace("円","")));
    }

    console.log(x_list);
    console.log(y_list);

    let colors = [];

    for (let value of y_list){
        if (value > 0){
            colors.push("rgb(0,200,0)");
        }
        else{
            colors.push("rgb(200,0,0)");
        }
    
    }


    const ctx = document.getElementById(canvas).getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: x_list,
            datasets: [{
                label:"収支",
                data: y_list,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },

        //これでグラフ上部のラベルを消す
        options: {
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });


}