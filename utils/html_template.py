HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css"/>
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.21/datatables.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>
  <style>
    {style}
  </style>
</head>
<body>
    {table}
<script>
    {script}
</script>
</body>
</html>
'''

STYLE = '''
tbody>tr>:nth-child(1),
tbody>tr>:nth-child(3),
tbody>tr>:nth-child(4),
tbody>tr>:nth-child(5),
tbody>tr>:nth-child(6),
tbody>tr>:nth-child(7)
{
 text-align:center;
}

#custom_table_wrapper {
  padding: 3rem 1rem;
}

div.dataTables_filter input {
  width: 300px !important;
}
'''

SCRIPT = '''
$(document).ready(function() {
    $('#custom_table').DataTable();
});
'''
