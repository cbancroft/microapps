<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Editing Object ###</title>
</head>
<body>
  <table>
    <tr py:for="c in columns">
      <td>${c}</td>
      <td>${getattr(record,c,None)}</td>
    </tr>
  </table>
</body>
</html>
