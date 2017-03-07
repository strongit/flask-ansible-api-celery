<script>
        function playbook() {
            $('#progress').empty();    
            $.ajax({
                type: 'POST',              // POST方式
                url: '/add',               // POST url
                data : $("#fuck").serialize(),  // POST数据(把表单数据id为fuck)
                success: function(data, status, request) {  
                    status_url = request.getResponseHeader('Location');  // POST成功后Flask会读取Locatio中带task.id的URL
                    update_progress(status_url);   // 调用update_progress函数去查询celery状态
                },
                error: function() {                // POST异常提示
                    alert('Unexpected error');
                }
            });
        }
        function update_progress(status_url) {
            $.getJSON(status_url, function(data) {   // 调用getJSON请求URL
                var txt = '';
                $.each(data.status, function(i, x){  // 循环分析get后的结果
                     txt += x;
                });
                $('#progress').text(txt);            // 将结果显示在id为progress处

                if (data['state'] == 'PENDING' || data['state'] == 'PROGRESS') {  // 2秒查询一次状态让判断celery task id的状态
                    setTimeout(function() { update_progress(status_url); }, 1000);  // 上面条件不匹配继续调用update_progress
                }
    
            });
        }
        $(function() {
            $('#start-bg-job').click(playbook);   //在id为start-bg-job处触发
        });
    </script>
