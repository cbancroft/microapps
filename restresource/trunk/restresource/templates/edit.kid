<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Edit</title>
</head>
<body>
  <div class="flash" py:if="tg_flash" py:content="tg_flash"></div>
  <div class="errors" py:if="tg_errors">Form Error!</div>
  ${form(value=record_dict, submit_text="Save", form_attrs=[('id',"%s_%s" % (form.name,record.id) )] )}
</body>
</html>
