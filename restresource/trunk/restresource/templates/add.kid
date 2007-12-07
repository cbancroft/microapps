<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Add</title>
</head>
<body>
  <div class="flash" py:if="tg_flash" py:content="tg_flash"></div>
  <div class="errors" py:if="tg_errors">Form Error!</div>
  ${form(submit_text="Save", form_attrs=[('id',form.name)])}
</body>
</html>
