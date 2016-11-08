-- Find the course code, teacher name, and average score of classes averaging a rating of 8 or above.
SELECT temp.course, temp.teacher, temp.avg FROM (SELECT c.course AS course, c.teacher AS teacher, avg(rating) as avg FROM Score_Reviews s, Class c WHERE s.class_id = c.id GROUP BY c.course, c.teacher) temp WHERE temp.avg >= 8.0 ORDER BY temp.course;
-- Find the course code and teacher name of classes with the tag "interesting".
SELECT c.course, c.teacher FROM Class c, Tag_Reviews r WHERE c.id = r.class_id AND tag IN (SELECT t.id FROM Tag t WHERE t.name = "interesting") ORDER BY c.course;