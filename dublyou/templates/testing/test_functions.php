<?php
    function test_func() {
        return "works";
    }
    function html_head($sheets=[], $scripts=[], $include="", $title="Test") {
        $static_root = "../../static";
        $stylesheets = array_merge(["bootstrap.min.css", "bootstrap-theme.min.css", "main.css"], $sheets);
        $scripts = array_merge(["vendor/modernizr-2.8.3-respond-1.4.2.min.js"], $scripts);

        $output = "<head>
                    <meta charset='utf-8'>
                    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
                    <meta name='viewport' content='width=device-width, initial-scale=1'>

                    <title>dublyou</title>

                    <link rel='icon' href=''>";

        foreach ($stylesheets as $sheet) {
            $output .= "\n<link rel='stylesheet' href='$static_root/css/$sheet'>";
        }

        foreach ($scripts as $script) {
            $output .= "\n<script src='$static_root/js/$script'></script>";
        }

        $output .= $include;
        return $output . "\n</head>";
    }

    function html_scripts($scripts=[]) {
        $static_root = "../../static";
        $scripts = array_merge(["vendor/bootstrap.min.js", "main.js"], $scripts);

        $output = "<script src='//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js'></script>
                    <script src='https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js'></script>";


        foreach ($scripts as $script) {
            
            $output .= "\n<script src='$static_root/js/$script'></script>";
        }

        return $output;
    }
?>