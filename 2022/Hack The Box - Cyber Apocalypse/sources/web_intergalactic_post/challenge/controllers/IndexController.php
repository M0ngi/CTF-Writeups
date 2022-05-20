<?php
class IndexController
{
    public function index($router)
    {
        return $router->view('index');
    }
}