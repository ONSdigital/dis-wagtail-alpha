import React from 'react';

interface TestReactProps {
    greeting: string;
}

/**
 * Tests that React is working in a new build.
 */
const TestReact = ({ greeting }: TestReactProps) => {
    const message = `The greeting is ${greeting}`;

    return (
        <div>
            <p className="test">{message}</p>
        </div>
    );
};

export default TestReact;
