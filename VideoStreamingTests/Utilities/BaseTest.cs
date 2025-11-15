using NUnit.Framework;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;

[TestFixture]
public class BaseTest
{
    protected IWebDriver Driver;

    protected TimeSpan WaitTime = ConfigurationManager.DefaultWaitTime;

    [SetUp]
    public void Setup()
    {
        Driver = new ChromeDriver();

        Driver.Manage().Window.Maximize();

        Driver.Navigate().GoToUrl(ConfigurationManager.BaseUrl);
    }

    [TearDown]
    public void TearDown()
    {
        Driver?.Quit();
    }
}