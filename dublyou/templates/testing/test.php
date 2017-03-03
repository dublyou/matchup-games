<!DOCTYPE html>
<html lang="en">
    <?php
    require 'test_functions.php';
    echo html_head([],[],'<link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css">');

    ?>
    <body>
    <?php echo file_get_contents("new_competition.html"); ?>
    <?php echo html_scripts(["bracket.js"]); ?>
    </body>
</html>