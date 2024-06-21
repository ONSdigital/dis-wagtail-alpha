import TbxForms from 'tbxforms';
import React from 'react';
import ReactDOM from 'react-dom';

import Carousel from './components/carousel';
import DesktopCloseMenus from './components/desktop-close-menus';
import DesktopSubMenu from './components/desktop-sub-menu';
import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';
import ProgressBar from './components/progress-bar';
import SkipLink from './components/skip-link';
import TableHint from './components/table-hint';
import Tabs from './components/tabs';
import TestReact from './components/TestReact';
import VideoModal from './components/video-modal';

// IE11 polyfills
import foreachPolyfill from './polyfills/foreach-polyfill';
import closestPolyfill from './polyfills/closest-polyfill';

import '../sass/main.scss';

foreachPolyfill();
closestPolyfill();

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-new */
    initComponent(Carousel);
    initComponent(DesktopSubMenu);
    initComponent(MobileMenu);
    initComponent(MobileSubMenu);
    initComponent(ProgressBar);
    initComponent(SkipLink);
    initComponent(TableHint);
    initComponent(Tabs);
    initComponent(TbxForms);
    initComponent(VideoModal);
    new DesktopCloseMenus();

    // Test react - add a div with a data attribute of `data-test-react` to test
    const items = document.querySelectorAll('[data-test-react]');
    items.forEach((element) => {
        ReactDOM.render(<TestReact greeting="boo!" />, element);
    });
});
