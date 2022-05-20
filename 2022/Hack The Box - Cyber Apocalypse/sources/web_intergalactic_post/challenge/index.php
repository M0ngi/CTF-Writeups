<?php
spl_autoload_register(function ($name){
    if (preg_match('/Controller$/', $name))
    {
        $name = "controllers/${name}";
    }
    else if (preg_match('/Model$/', $name))
    {
        $name = "models/${name}";
    }
    include_once "${name}.php";
});


$database = new Database('/tmp/challenge.db');

$router = new Router();
$router->new('GET', '/', 'IndexController@index');
$router->new('POST', '/subscribe', 'SubsController@store');

die($router->match());