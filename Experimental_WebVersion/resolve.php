<?php
if(isset($_GET['ip'])){
    $ip = $_GET['ip'];
    $hostname = gethostbyaddr($ip);
    echo $hostname ? $hostname : "N/A";
} else {
    echo "N/A";
}
?>
