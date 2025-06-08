create view HaifaApp as
    select aName
    from Applications A1
    where A1.isInstalled=1 and exists (select *
                                     from AppUsers AU1
                                     inner join Contacts C1
                                     on AU1.cName=C1.cName
                                     where A1.aName = AU1.aName and C1.city = 'Haifa'
                                     );


create view AverageRating as
select AU.aName, A1.aCategory, round(cast(avg(1.0 * AU.rating) as float), 2) as avg_rating
from AppUsers AU
inner join Applications A1
on AU.aName=A1.aName
group by AU.aName, A1.aCategory;


create view LeadingApps as
select A1.aName
from Applications A1
inner join AppUsers AU1
on A1.aName=AU1.aName
inner join AverageRating AR
on AR.aName=A1.aName
where AR.avg_rating = (select max(AR2.avg_rating)
                       from AverageRating AR2
                       where AR.aCategory = AR2.aCategory)
and A1.aName in (select AU2.aName
                 from AppUsers AU2
                 group by AU2.aName
                 having count(*) >= 22);


create view InstalledLeadAppsCount as
select AU1.cName, count(distinct AU1.aName) as leadAppCount
from AppUsers AU1
inner join LeadingApps LA1
on AU1.aName = LA1.aName
group by AU1.cName
union
select C.cName, 0 as leadAppCount
from Contacts C
where C.cName not in (
    select AU2.cName
    from AppUsers AU2
    inner join LeadingApps LA2
    on AU2.aName = LA2.aName
);


create view BeyondCities as
select distinct C1.city
from Contacts C1
left join (
    select C2.city
    from Contacts C2
    where C2.cName NOT IN (
        select AU1.cName
        from AppUsers AU1
        inner join Applications A1
        on AU1.aName = A1.aName
        group by AU1.cName
        having sum(aSize) > 1200
    )
) as FilteredCities
on C1.city = FilteredCities.city
where FilteredCities.city IS NULL;


create view InstallationCount as
    select BC1.city as city, AU1.aName as aName, count(*) as count
    from BeyondCities BC1
    inner join Contacts C1
    on BC1.city = C1.city
    inner join AppUsers AU1
    on AU1.cName = C1.cName
    group by BC1.city, AU1.aName
    having count(*) > 2;